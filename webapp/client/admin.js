"use strict"





function list_count(list) {
    if (list) return list.length
    return 0
}

var DISPLAY_FORMATS = {
    start_time: 'DateTime',
    end_time: 'DateTime',
    percent_done: '(0.00 %)',
    errors: list_count,
    errors_http: list_count,
    warnings: list_count
}

var taskView = undefined;


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

var app = undefined;
function createComponents() {
    Vue.use(Vuetify)

    app = new Vue({
      el: '#vueApp',
      data: {

          // TODO: what's the proper way to deal with lazy loading?
          tableDataSimple: [],
          selected: {},
          headers: [
          { text: 'Name', value: 'name'},
          { text: 'Start Time', value: 'start_time' },
          { text: 'Running', value: 'running' },
          { text: 'Failed', value: 'failed' },
          { text: 'Canceled', value: 'canceled' },

        ],
        items: [],
        search: "",
      },

      mounted: function() {
          var self = this
          $.getJSON('/api/ingestion_tasks?running=false', function (json) {
              self.tableDataSimple = json;
              self.selected = self.tableDataSimple[0]
              self.items = json;

          });
      }
    });
}


$(document).ready(function () {

    createComponents()


    /*runningTaksTable = new RunningTaskTable("runningTasksTable")
    completedTasksTable = new CompletedTaskTable("completedTasksTable")

    updateTasks()*/
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
        completedTasksTable.setData(tasks);

        var taskNames = {}
        tasks.forEach(function(task) {
            taskNames[task.name] = 1;
        });

        var select = $("#taskSelect");
        for (var name in taskNames) {
            var op = $("<option>", {value: name});
            op.html(name);

            select.append(op);
        }

        function showFor(name) {
            var coinlistTasks = tasks.filter(function(task){
                return task.name == name;
            });
            buildChart(name, coinlistTasks);
        }

        select.change(function(val) {
            name = select.val();
            showFor(name);
        });

        showFor("ImportCoinList")

        taskView = new TaskView(tasks[0])
        taskView.render()

        var parent = $("#taskDetails");
        parent.append(taskView._container)
    });
}


function updateTasks() {
    updateRunningTasks();
    //setInterval(updateRunningTasks, 5000);

    updateCompletedTasks();
}





function buildChart(name, tasks) {
    function toSeries(key) {
        var points = [];
        tasks.forEach(function (task) {
            points.push([task.start_time, task[key]]);
        });

        return points;
    }

    var errors = toSeries("errors");
    var httpErrors = toSeries("errors_http");
    var warnings = toSeries("warnings");


    Highcharts.chart('chart', {
    chart: {
        type: 'spline'
    },
    title: {
        text: 'Errors over time'
    },
    subtitle: {
        text: 'task ' + name
    },
    xAxis: {
        type: 'datetime',
        dateTimeLabelFormats: { // don't display the dummy year
            month: '%e. %b',
            year: '%b'
        },
        title: {
            text: 'Date'
        }
    },
    yAxis: {
        title: {
            text: 'Count'
        },
        min: 0
    },
    tooltip: {
        headerFormat: '<b>{series.name}</b><br>',
        pointFormat: '{point.x:%e. %b}: {point.y:.2f} m'
    },

    plotOptions: {
        spline: {
            marker: {
                enabled: true
            }
        }
    },

    series: [{
            name: "Errors",
            data: errors
        }, {
            name: "HTTP Errors",
            data: httpErrors
        }, {
            name: "Warnings",
            data: warnings
        }]
});
}



class TaskView extends Component {
    constructor(task) {
        super();
        this._task = task;
    }

    render() {



        var self = this
        function line(name, key) {
            return `<br/>${name}: ${self._task[key]}`
        }

        var html = line("Name", "name");
        html += line("Start Time", "start_time");
        html += line("Elapsed Time", "elapsed_time");

        function error_list(name, errors) {
            html = `<hX>${name}(${errors.length})</hX>`
            html += "<ul>"

            errors.forEach(function(error) {
                html += "<li>"
                html += error
                html += "</li>"
            });

            html += "</ul>"
            return html
        }

        html += "<br/>"
        html += error_list("Errors", this._task.errors);
        html += error_list("Warnings", this._task.warnings);
        html += error_list("HTTP Errors", this._task.errors_http);

        this._container.append(html);
    }
}
