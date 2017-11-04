var url = "/api/ingestion_tasks"


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
            {header: "Errors", key: "errors"},
            {header: "Warnings", key: "warnings"},
            {header: "% Complete", key: "percent_done"},
            {header: "Failed", key: "failed"},
            {header: "DB inserts", key: "db_inserts"},
        ]);


        super.setData(stats, DISPLAY_FORMATS);
    }
}

$(document).ready(function () {
    table = new CoinStatsTable("taskTable")

    console.log("fetching ingestion tasks")
    $.getJSON(url, function (data) {
        console.log(data)
        table.setData(data._items)
    });
});
