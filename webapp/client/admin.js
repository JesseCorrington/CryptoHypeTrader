var DISPLAY_FORMATS = {
    start_time: 'DateTime',
    end_time: 'DateTime',
    percent_done: '(0.00 %)',
}


class RunningTaskTable extends Table {
    constructor(cointainer, width, height) {
        super(cointainer, width, height);

        super.setColumns([
            // TODO: we could set cols in the ctor
            {header: "Name", key: "name"},
            {header: "Start Time", key: "start_time"},
            {header: "Elapsed", key: "elapsed_time"},
            {header: "Errors", key: "errors"},
            {header: "HTTP Errors", key: "errors_http"},
            {header: "Warnings", key: "warnings"},
            {header: "% Complete", key: "percent_done"},
            {header: "HTTP requests", key: "http_requests"},
            {header: "DB inserts", key: "db_inserts"},
        ]);
    }

    setData(stats) {
        super.setData(stats, DISPLAY_FORMATS);
    }
}

class CompletedTaskTable extends Table {
    constructor(cointainer, width, height) {
        super(cointainer, width, height);

        super.setColumns([
            // TODO: we could set cols in the ctor
            {header: "Name", key: "name"},
            {header: "Start Time", key: "start_time"},
            {header: "Elapsed", key: "elapsed_time"},
            {header: "Failed", key: "failed"},
            {header: "Canceled", key: "canceled"},
            {header: "Errors", key: "errors"},
            {header: "HTTP Errors", key: "errors_http"},
            {header: "Warnings", key: "warnings"},
            {header: "% Complete", key: "percent_done"},
            {header: "HTTP requests", key: "http_requests"},
            {header: "DB inserts", key: "db_inserts"},
        ]);
    }

    setData(stats) {
        super.setData(stats, DISPLAY_FORMATS);
    }
}

var runningTaksTable = undefined;
var completedTasksTable = undefined;

$(document).ready(function () {
    runningTaksTable = new RunningTaskTable("runningTasksTable")
    completedTasksTable = new CompletedTaskTable("completedTasksTable")

    updateTasks()
});

function processTasks(tasks) {
    tasks.forEach(
        function(task) {
            task.elapsed_time = task.end_time? task.end_time - task.start_time :
                task.last_update - task.start_time;

            // Convert to seconds
            task.elapsed_time = Math.round(task.elapsed_time / 1000);
    });
}


function updateRunningTasks() {
    $.getJSON('/api/ingestion_tasks?running=true', function (tasks) {
        processTasks(tasks);
        runningTaksTable.setData(tasks);
    });
}

function updateCompletedTasks() {
    $.getJSON('/api/ingestion_tasks?running=false', function (tasks) {
        processTasks(tasks);
        completedTasksTable.setData(tasks)
    });
}


function updateTasks() {
    updateRunningTasks();
    setInterval(updateRunningTasks, 5000);

    updateCompletedTasks();
}
