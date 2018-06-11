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
                  <v-icon>cancel</v-icon>
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
  </div>
</template>

<script>
import Services from '@/services/Services'

export default {
    name: 'Admin',

    data () {
        return {
            headers: [
                {text: 'Running', value: 'running', align: 'left'},
                {text: 'Progress', value: 'running', align: 'left'},
                {text: 'Cancel', value: 'running', align: 'left'},
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
                sortBy: 'running',
                descending: true
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
        }
    }
}
</script>
