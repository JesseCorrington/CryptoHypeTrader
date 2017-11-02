console.log("starting client app");

var pending = 2
var chartData = []

function buildcharts() {
    Highcharts.stockChart('container', {

        rangeSelector: {
            selected: 1
        },

        title: {
            text: 'subscribers'
        },

        series: chartData
    });
}

function get_stats() {
    $.getJSON("/api/social_stats", function (data) {
        var symbol = data._items[0].symbol

        series = []

        for (var i in data._items) {
            var date = new Date(data._items[i].date).getTime()
            var price = parseFloat(data._items[i].subscribers)

            series.push([date, price])
        }

        chartData.push({
            name: symbol + " reddit subs",
            data: series
        });

        pending--;
        if (pending == 0) {
            buildcharts()
        }
    });
}


function get_prices() {
    $.getJSON("/api/prices", function (data) {
        var symbol = data._items[0].symbol

        series = []

        for (var i in data._items) {
            var date = new Date(data._items[i].date).getTime()
            var price = parseFloat(data._items[i].close)

            series.push([date, price])
        }

        // chartData.push({
        //     name: symbol + " price",
        //     data: series
        // });

        pending--;
        if (pending == 0) {
            buildcharts()
        }
    });
}

get_stats()
get_prices()