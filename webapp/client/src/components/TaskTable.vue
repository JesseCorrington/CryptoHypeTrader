<template>
<v-data-table
    :headers="headers"
    :items="tasks"
    :rows-per-page-items="[20,50]"
    :pagination.sync="pagination"
    class="elevation-1"
    item-key="_id">

    <template slot="headerCell" slot-scope="props">
        <strong>{{ props.header.text }}</strong>
    </template>

    <template slot="items" slot-scope="props">
        <td align="left"><a @click="showDetails(props.item.name)" class="link">{{props.item.name}}</a></td>

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
</template>

<script>
    export default {
        name: "TaskTable",

        props: ["tasks"],

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
                pagination: {
                    sortBy: 'start_time',
                    descending: true
                }
            }
        },

        methods: {
            showDetails(name) {
                this.$emit('task-select', name)
            }
        }
    }
</script>

<style scoped>

</style>
