"use strict"


Vue.use(Vuetify)

var tasksByType = {}

var app = new Vue({
  el: '#vueApp',
  data: {
      headers: [
          { text: 'Name', value: 'name', align: "left"},
          { text: 'Start Time', value: 'start_time' },
          { text: 'Elapsed Time', value: 'elapsed_time' },
          { text: 'Running', value: 'running' },
          { text: 'Last Update', value: 'last_update' },
          { text: 'Percent Complete', value: 'percent_done' },
          { text: 'Failed', value: 'failed' },
          { text: 'Canceled', value: 'canceled' },
          { text: 'Errors', value: 'errors' },
          { text: 'Warnings', value: 'warnings' },
          { text: 'HTTP Errors', value: 'errors_http' },
          { text: 'HTTP Requests', value: 'http_requests' },
          { text: 'DB Inserts', value: 'db_inserts' },
          { text: 'DB Updates', value: 'db_updates' },
        ],
      items: [],
      selected: [],
      search: "",
      pagination: {
          sortBy: "start_time",
          descending: true
      },
      taskTypes: [],
      selectedSeries: "ImportPrices"
  },

  mounted: function() {
      var self = this
      $.getJSON('/api/ingestion_tasks', function (json) {
          self.items = json;

          json.forEach(function(task) {
              task.elapsed_time = task.last_update - task.start_time;
              if (!tasksByType[task.name]) {
                  tasksByType[task.name] = []
              }
              tasksByType[task.name].push(task);
          });

          self.taskTypes = Object.keys(tasksByType);

          buildTaskChart(self.selectedSeries, tasksByType[self.selectedSeries])
      });

      $.getJSON('/api/db_stats', buildDBStatsChart);
  },

    watch: {
      selectedSeries: function() {
          buildTaskChart(this.selectedSeries, tasksByType[this.selectedSeries])
      }
    }
});


var charts = {};

function toSeries(objs, key) {
    var series = [];
    objs.forEach(function (task) {
        var val = task[key];
        if (val.length !== undefined) {
            val = val.length;
        }

        series.push([task.start_time, val]);
    });

    return series;
}

function buildChart(container, title, subTitle, data, series) {
    if (!charts[title]) {
        charts[title] = Highcharts.chart(container, {
            chart: {
                type: 'line'
            },
            title: {
                text: title
            },
            subtitle: {
                text: subTitle
            },
            xAxis: {
                type: 'datetime',
                dateTimeLabelFormats: {
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
            }
        });
    }
    else {
        // Just need to update the title
        charts[title].setTitle({text: title}, {text: subTitle});
    }

    // remove all existing series
    while(charts[title].series.length > 0) {
        charts[title].series[0].remove(true);
    }

    for (var dispName in series) {
        var key = series[dispName];
        charts[title].addSeries({
            name: dispName,
            data: toSeries(data, key)
        });
    }
}


function buildTaskChart(name, data) {
    var series = {
        "Errors": "errors",
        "HTTP Errors": "errors_http",
        "Warnings": "warnings",
        "HTTP Requests": "http_requests",
        "DB Inserts": "db_inserts",
        "DB_Updates": "db_updates"
    };

    buildChart("taskChart", "Task Runs", name, data, series);
}


function buildDBStatsChart(data) {
    var series = {
        "Objects": "objects",
        "Storage Size": "storageSize",
        "indexSize": "indexSize"
    };

    buildChart("dbStatsChart", "Database Storage", "", data, series);
}
