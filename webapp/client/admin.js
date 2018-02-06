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
          sortBy: 'start_time'
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

          buildChart(self.selectedSeries, tasksByType[self.selectedSeries])
      });

      $.getJSON('/api/db_stats', function (json) {
          console.log(json);
      })
  },

    watch: {
      selectedSeries: function() {
          buildChart(this.selectedSeries, tasksByType[this.selectedSeries])
      }
    }
});


var chart = undefined;

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

function buildChart(name, data) {
    if (!chart) {
        chart = Highcharts.chart('chartContainer', {
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

    // remove all existing series
    for (var i = 0; i < 6; i++) {
        var s = chart.get(i);
        if (s) {
            s.remove();
        }
    }

    chart.addSeries({
        id: 0,
        name: "Errors",
        data: toSeries(data, "errors")
    });

    chart.addSeries({
        id: 1,
        name: "HTTP Errors",
        data: toSeries(data, "errors_http")
    });

    chart.addSeries({
        id: 2,
        name: "Warnings",
        data: toSeries(data, "warnings")
    });

    chart.addSeries({
        id: 3,
        name: "HTTP Requests",
        data: toSeries(data, "http_requests")
    });

    chart.addSeries({
        id: 4,
        name: "DB Inserts",
        data: toSeries(data, "db_inserts")
    });

    chart.addSeries({
        id: 5,
        name: "DB Updates",
        data: toSeries(data, "db_updates")
    });
}


function buildDBStatsChart() {

}
