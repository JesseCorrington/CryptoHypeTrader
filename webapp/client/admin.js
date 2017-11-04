var DISPLAY_FORMATS = {
    start_time: 'DateTime',
    end_time: 'DateTime',
    percent_done: '(0.00 %)',
}


class CoinStatsTable extends Table {
    constructor(cointainer, width, height) {
        super(cointainer, width, height);
    }

    setData(stats) {
        super.setColumns([
            // TODO: we could set cols in the ctor
            {header: "Name", key: "name"},
            {header: "Start Time", key: "start_time"},
            {header: "End Time", key: "end_time"},
            {header: "Running", key: "running"},
            {header: "Canceled", key: "canceled"},
            {header: "Errors", key: "errors"},
            {header: "Warnings", key: "warnings"},
            {header: "% Complete", key: "percent_done"},
            {header: "Failed", key: "failed"},
            {header: "DB inserts", key: "db_inserts"},
        ]);


        super.setData(stats, DISPLAY_FORMATS);
    }
}

// TODO: only set true if one task is running
taskRunning = true
var table = undefined

//var running = '/api/ingestion_tasks?where={"running": true}'
var url = '/api/ingestion_tasks'

$(document).ready(function () {
    table = new CoinStatsTable("taskTable")

    // TODO: remove this hack to force refresh of data
    updateTasks()
    //setInterval(updateTasks, 1000)
});

// TODO: it's really inefficient to get the whole task list, just to track the running one
// but good enough for now
function updateTasks() {
    $.getJSON(url, function (data) {
        table.setData(data._items)
    });
}
