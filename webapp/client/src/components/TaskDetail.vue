<template>
<div>
    Details for task {{taskname}}

    <v-card>
        <task-table :tasks="tasks"></task-table>
    </v-card>

    <div ref="stockChart"></div>
</div>
</template>

<script>
    import Services from '@/services/Services'
    import Task from "@/models/Task"

    export default {
        name: "TaskDetail",
        props: ["taskname"],

        data () {
            return {
                tasks: [],
            }
        },

        mounted () {
            this.getTasks();
        },

        methods: {
            async getTasks () {
                const response = await Services.getIngestionTasks(this.taskname);
                this.tasks = response.data

                // Add computed properties to help build the UI
                for (var i = 0; i < this.tasks.length; i++) {
                    this.tasks[i] = new Task(this.tasks[i]);
                }
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

<style scoped>

</style>
