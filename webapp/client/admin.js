"use strict"


Vue.use(Vuetify)


var app = new Vue({
  el: '#vueApp',
  data: {
      // TODO: what's the proper way to deal with lazy loading?
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
      }
  },

  mounted: function() {
      var self = this
      $.getJSON('/api/ingestion_tasks', function (json) {
          self.items = json;

          json.forEach(function(task) {
             task.elapsed_time = task.start_time - task.a_time;
          });
      });
  }
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
