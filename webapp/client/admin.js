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

          buildChart("CreateCoinSummaries")
      });
  },

    watch: {
      selectedSeries: function() {
          console.log("on chnage " + this.selectedSeries);
      }
    }
});


function buildChart(name) {
    function toSeries(key) {
        var series = [];
        tasksByType[name].forEach(function (task) {
            var val = task[key];
            if (val.length !== undefined) {
                val = val.length;
            }

            series.push([task.start_time, val]);
        });

        return series;
    }

    var errors = toSeries("errors");
    var httpErrors = toSeries("errors_http");
    var warnings = toSeries("warnings");


    Highcharts.chart('chartContainer', {
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
