<template>
<div>
    Details for task {{taskname}}
    <div ref="stockChart"></div>
</div>
</template>

<script>
    export default {
        name: "TaskDetail",

        props: ["taskname"],

        methods: {
            async getTasks () {
                // const response = await Services.getIngestionTasks()
                // this.tasks = response.data
                //
                // // Add computed properties to help build the UI
                // for (var i = 0; i < this.tasks.length; i++) {
                //     var endTime = this.tasks[i].running ? new Date().getTime() : this.tasks[i].end_time;
                //     this.tasks[i].elapsed_time = endTime - this.tasks[i].start_time;
                //     this.tasks[i].percent_done *= 100;
                //
                //     if (this.tasks[i].failed || this.tasks[i].canceled) {
                //         this.tasks[i].statusIcon = 'error'
                //         this.tasks[i].statusIconColor = 'red'
                //         this.tasks[i].statusIconTooltip = this.tasks[i].failed ? 'failed' : 'canceled'
                //     } else {
                //         this.tasks[i].statusIcon = 'done'
                //         this.tasks[i].statusIconTooltip = 'success'
                //     }
                // }
                //
                // var coinlistTasks = this.tasks.filter(function(task){
                //     return task.name == "ImportCoinList";
                // });
                // this.buildChart("ImportCoinList", coinlistTasks);
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
