<template>
<div>
    <h1>Ingestion Tasks</h1>

    <div v-if="!detailsVisible">
        <v-card>
            <task-table :tasks="tasks" @task-select="showDetails"></task-table>
        </v-card>
    </div>
    <div v-else>
        <task-detail :taskname="detailsTaskName"></task-detail>
    </div>
</div>
</template>

<script>
    import Services from '@/services/Services'
    import TaskDetail from "./TaskDetail";

    export default {
        name: 'Admin',
        components: {TaskDetail},
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
                detailsVisible: false,
                detailsTaskName: undefined,
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

            showDetails(name) {
                this.detailsVisible = true;
                this.detailsTaskName = name;
            },

            hideDetails(name) {
                this.detailsVisible = false;
                this.detailsTaskName = undefined
            }
        }
    }
</script>
