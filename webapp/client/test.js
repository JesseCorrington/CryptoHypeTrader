console.log("starting client app");

var pending = 2
var chartData = []

function buildSingleChart() {
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

function buildCompareChart() {
    Highcharts.stockChart('container', {

        rangeSelector: {
            selected: 4
        },

        yAxis: {
            labels: {
                formatter: function () {
                    return (this.value > 0 ? ' + ' : '') + this.value + '%';
                }
            },
            plotLines: [{
                value: 0,
                width: 2,
                color: 'silver'
            }]
        },

        plotOptions: {
            series: {
                compare: 'percent',
                showInNavigator: true
            }
        },

        tooltip: {
            pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.change}%)<br/>',
            valueDecimals: 2,
            split: true
        },


        series: chartData
    });
}


function get_stats() {
    var url = "/api/social_stats" + '?where={"symbol": "eth"}'

    $.getJSON(url, function (data) {
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
            buildCompareChart()
        }
    });
}


function get_prices() {
    var url = "/api/prices" + '?where={"symbol": "eth"}'

    $.getJSON(url, function (data) {
        var symbol = data._items[0].symbol

        series = []

        for (var i in data._items) {
            var date = new Date(data._items[i].date).getTime()
            var price = parseFloat(data._items[i].close)

            series.push([date, price])
        }

        chartData.push({
            name: symbol + " price",
            data: series
        });

        pending--;
        if (pending == 0) {
            buildCompareChart()
        }
    });
}

get_stats()
get_prices()