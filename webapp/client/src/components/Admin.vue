<template>
  <div>
      <h1>Ingestion Tasks</h1>
      <v-card>
      <v-data-table
          :headers="headers"
          :search="search"
          :pagination.sync="pagination"
          :items="tasks"
          :rows-per-page-items="[10,20,50,100]"
          v-model="selected"
          class="elevation-1"
          item-key="_id"
          select-all>

          <template slot="items" slot-scope="props">
              <td><v-checkbox primary hide-details v-model="props.selected"></v-checkbox></td>
              <td align="left">{{props.item.name}}</td>

              <td v-if="props.item.running">
                    <v-progress-linear v-model="props.item.percent_done"/>
              <td v-else>
                  <v-tooltip top>
                      <v-icon slot="activator" :color="props.item.statusIconColor">{{props.item.statusIcon}}</v-icon>
                      <span>{{props.item.statusIconTooltip}}</span>
                  </v-tooltip>
              </td>

              <td v-if="props.item.running">
                  <v-btn flat icon @click="cancelTask(props.item._id)">
                      <v-icon>cancel</v-icon>
                  </v-btn>
              </td>
              <td v-else/>

              <td align="left">{{props.item.start_time | dateTime}}</td>
              <td align="left">{{props.item.elapsed_time | timeInterval}}</td>
              <td align="left">{{props.item.errors.length}}</td>
              <td align="left">{{props.item.errors_http.length}}</td>
              <td align="left">{{props.item.db_inserts}}</td>
              <td align="left">{{props.item.db_updates}}</td>
          </template>
      </v-data-table>
      </v-card>

      <div ref="stockChart"></div>
  </div>
</template>

<script>
import Services from '@/services/Services'
import Highcharts from 'highcharts'

export default {
    name: 'Admin',

    data () {
        return {
            headers: [
                {text: 'Name', value: 'name', align: 'left'},
                {text: 'Progress', value: 'percent_done', align: 'left'},
                {text: 'Cancel', value: '', align: 'left', sortable: false},
                {text: 'Start Time', value: 'start_time', align: 'left'},
                {text: 'Elapsed Time', value: 'elapsed_time', align: 'left'},
                {text: 'Errors', value: 'errors', align: 'left'},
                {text: 'HTTP Errors', value: 'errors_http', align: 'left'},
                {text: 'DB Inserts', value: 'db_inserts', align: 'left'},
                {text: 'DB Updates', value: 'db_updates', align: 'left'}
            ],
            tasks: [],
            search: '',
            selected: [],
            pagination: {
                sortBy: 'percent_done',
                descending: false
            }
        }
    },

    mounted () {
        this.getTasks()
    },

    methods: {
        async getTasks () {
            const response = await Services.getIngestionTasks()
            this.tasks = response.data

            // Add computed properties to help build the UI
            for (var i = 0; i < this.tasks.length; i++) {
                var endTime = this.tasks[i].running ? new Date().getTime() : this.tasks[i].end_time;
                this.tasks[i].elapsed_time = endTime - this.tasks[i].start_time;
                this.tasks[i].percent_done *= 100;

                if (this.tasks[i].failed || this.tasks[i].canceled) {
                    this.tasks[i].statusIcon = 'error'
                    this.tasks[i].statusIconColor = 'red'
                    this.tasks[i].statusIconTooltip = this.tasks[i].failed ? 'failed' : 'canceled'
                } else {
                    this.tasks[i].statusIcon = 'done'
                    this.tasks[i].statusIconTooltip = 'success'
                }
            }


            var coinlistTasks = this.tasks.filter(function(task){
                return task.name == "ImportCoinList";
            });
            this.buildChart("ImportCoinList", coinlistTasks);
        },

        async cancelTask(id) {
            const response = await Services.cancelIngestionTask(id);
            this.success = response.data
        },

        buildChart(name, tasks) {
            function toSeries(key) {
                var points = [];
                tasks.forEach(function (task) {
                    var val = task[key];
                    if (val.constructor == Array) {
                        val = val.length
                    }
                    points.push([task.start_time, val]);
                });

                return points;
            }

            var errors = toSeries("errors");
            var httpErrors = toSeries("errors_http");
            var warnings = toSeries("warnings");
            var dbInserts = toSeries("db_inserts");
            var dbUpdates = toSeries("db_updates");

            this.chart = Highcharts.stockChart(this.$refs.stockChart, {
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
                series: [{
                    name: "Errors",
                    data: errors
                }, {
                    name: "HTTP Errors",
                    data: httpErrors
                }, {
                    name: "Warnings",
                    data: warnings
                }, {
                    name: "DB Inserts",
                    data: dbInserts
                }, {
                    name: "DB Updates",
                    data: dbUpdates
                }]
            });
        }

    }
}
</script>
