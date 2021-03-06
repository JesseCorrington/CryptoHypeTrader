import datetime
import sys
import os

from common import database as db
from ingestion import config
from ingestion import datasource as ds


class FatalError(Exception):
    """"An unrecoverable error that requires ingestion to halt"""
    pass


class IngestionTask:
    """An abstract base class for all data ingestion tasks

    This provides tracking for long running back ground tasks
        (http requests, errors, warning, db inserts/updates, etc.)
    Derived classes should funnel all http and database interaction through
    helper methods (ie: _get_data, _db_insert) to ensure proper tracking.
    Task status is saved to the ingestion_tasks database table.
    """

    def __init__(self):
        self._name = type(self).__name__
        self.__id = None

        # Status
        self.__running = False
        self.__start_time = None
        self.__end_time = None
        self.__percent_done = 0.0
        self.__failed = False
        self.__canceled = False

        # Error tracking
        self.__errors = []
        self.__errors_http = []
        self.__warnings = []

        # Profiling
        self.__db_inserts = 0
        self.__db_updates = 0
        self.__http_requests = 0

        # Track PID for cancellation
        self.__pid = os.getpid()

    def __str__(self):
        return "{} - running={}, errors={}, warnings={}".\
            format(self._name, self.__running, len(self.__errors), len(self.__warnings))

    def _error(self, msg):
        """"Derived classes call to signal an error"""

        print("Ingestion error:", msg)
        self.__errors.append(msg)

    def __error_http(self, msg):
        """Only for the base class to use, since it manages all HTTP requests"""

        print("Ingestion HTTP error:", msg)
        self.__errors_http.append(msg)

    def _fatal(self, msg, raise_error=True):
        """Derived classes call to raise a FatalError, which
        will stop the tasks run function, and bring control back to the manager
        """

        print("Ingestion FATAL error:", msg)
        self._error("FATAL - " + msg)
        self.__failed = True

        if raise_error:
            raise FatalError(msg)

    def _warn(self, msg):
        """Derived classes call to signal a warning"""

        print("Ingestion warning:", msg)
        self.__warnings.append(msg)

    def _progress(self, completed, total):
        """Derived classes call to signal status updates"""
        self.__percent_done = completed / total

        now = datetime.datetime.utcnow()
        elapsed = now - self.__start_time
        avg_time_per = elapsed / completed
        est_time_left = (avg_time_per * (total - completed))

        print("Progress {}/{} - est. time remaining {}".format(completed, total, est_time_left))

        self.__update_db_status()

    def _run(self):
        """Derived classes implement the task here"""
        raise NotImplementedError("Subclass must implement _run method")

    def _db_insert(self, collection, items):
        """Derived classes call to insert item(s) into the database"""
        try:
            db.insert(collection, items)
            count = len(items) if isinstance(items, list) else 1
            self.__db_inserts += count
        except Exception as err:
            self._error("Database insert failed: " + str(err))

    def _db_update_one(self, collection, doc_id, updates):
        """Derived classes call to update a single database record"""
        try:
            db.mongo_db[collection].update_one({
                '_id': doc_id
            }, {
                '$set': updates
            }, upsert=False)
            self.__db_updates += 1
        except Exception as err:
            self._error("Database update failed: " + str(err))

    def _get_data(self, datasource, arg=None):
        """Derived classes call to get data from a DataSource instance

        :param datasource: a DataSource instance or a function to get the data
        :return: The data, or none if there was an error
        """
        self.__http_requests += 1

        data = None
        try:
            data = datasource(arg) if callable(datasource) else datasource.get()
        except ds.ParseError as err:
            self._error("DataSource Parse error - {} - {}".format(datasource.url, err))
        except (ds.HTTPError, ds.ValidationError) as err:
            self.__error_http("{} - {}".format(datasource.url, err))
        except Exception as err:
            self._error("Unknown get_data error {}".format(err))

        return data

    def __update_db_status(self):
        """Updates the current status of the task in the database"""

        now = datetime.datetime.utcnow()

        status = {
            "name": self._name,
            "start_time": self.__start_time,
            "end_time": self.__end_time,
            "running": self.__running,
            "errors": self.__errors,
            "errors_http": self.__errors_http,
            "warnings": self.__warnings,
            "percent_done": self.__percent_done,
            "failed": self.__failed,
            "db_inserts": self.__db_inserts,
            "db_updates": self.__db_updates,
            "http_requests": self.__http_requests,
            "canceled": self.__canceled,
            "last_update": now
        }

        if self.__running:
            status["pid"] = self.__pid

        try:
            if self.__id is None:
                self.__id = db.mongo_db.ingestion_tasks.insert(status)
            else:
                db.mongo_db.ingestion_tasks.replace_one({'_id': self.__id}, status)
        except Exception as e:
            self._error("Failed to update db status for ingestion tasks: " + str(e))

    def cancel(self):
        """Cancel the task
        Note that this just sets the tasks status and updates the db tracking it
        It's still the responsibility of the code running the task to terminate it
        """

        self.__running = False
        self.__canceled = True
        self.__end_time = datetime.datetime.utcnow()

        self.__update_db_status()

    def run(self):
        """Run the task"""

        self.__running = True
        self.__start_time = datetime.datetime.utcnow()

        print("Running ingestion task:", self._name)
        self.__update_db_status()

        try:
            self._run()
        except FatalError:
            print("Task stopped due to fatal error")
        except Exception as err:
            # Catch all so that we don't kill our process when running live
            self._fatal("Unhandled exception {}".format(err), False)

            # Re-raise in dev mode for easier debugging
            if config.dev:
                raise err

        self.__end_time = datetime.datetime.utcnow()
        self.__running = False
        self.__percent_done = 1.0
        self.__update_db_status()

        elapsed_time = self.__end_time - self.__start_time

        sf = "Failure" if self.__failed else "Success"
        print("Ingestion task {} ({})".format(self._name, sf))
        print("Elapsed time:", elapsed_time)
        print("HTTP requests:", self.__http_requests)
        print("Database inserts:", self.__db_inserts)
        print("Database updates:", self.__db_updates)

        def print_errors(name, error_list):
            print("{} ({}):".format(name, len(error_list)))
            for msg in error_list:
                print("  *", msg)

        print_errors("Errors", self.__errors)
        print_errors("HTTP Errors", self.__errors_http)
        print_errors("Warnings", self.__warnings)


def run_tasks(tasks):
    """ Run tasks
    :param tasks: a single task or list of tasks
    """

    if not isinstance(tasks, list):
        tasks = [tasks]

    if not db.connected():
        print("Database not connected, exiting")
        return

    start_time = datetime.datetime.utcnow()

    for task in tasks:
        try:
            task.run()
        except (KeyboardInterrupt, SystemExit):
            task.cancel()
            sys.exit()

    end_time = datetime.datetime.utcnow()
    elapsed_time = end_time - start_time

    print("Ingestion complete, elapsed time:", elapsed_time)
