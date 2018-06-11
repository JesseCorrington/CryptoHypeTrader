<template>
  <div>
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
                {text: 'Name', value: 'name', align: 'left'},
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
                sortBy: 'start_time',
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

            for (var i = 0; i < this.tasks.length; i++) {
                this.tasks[i].elapsed_time = this.tasks[i].end_time - this.tasks[i].start_time;
            }
        }
    }
}
</script>
