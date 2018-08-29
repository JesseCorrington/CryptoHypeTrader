<template>
<div>
    <div v-if="!detailsVisible">
        <h2>Ingestion Tasks</h2>

        <v-card>
            <task-table :tasks="tasks" @task-select="showDetails"></task-table>
        </v-card>
    </div>
    <div v-else>
        <h2><v-btn flat @click="hideDetails"><v-icon>arrow_back_ios</v-icon>Back</v-btn> All runs of {{detailsTaskName}} </h2>

        <task-detail :taskname="detailsTaskName"></task-detail>
    </div>
</div>
</template>

<script>
    import Services from '@/services/Services'
    import Task from "@/models/Task"
    import TaskDetail from "./TaskDetail";

    export default {
        name: 'Admin',
        components: {TaskDetail},
        data () {
            return {
                tasks: [],
                detailsVisible: false,
                detailsTaskName: undefined,
            }
        },

        mounted () {
            this.getTasks();
        },

        methods: {
            async getTasks () {
                const response = await Services.getIngestionTasks()
                this.tasks = response.data

                // Add computed properties to help build the UI
                for (var i = 0; i < this.tasks.length; i++) {
                    this.tasks[i] = new Task(this.tasks[i]);
                }
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
