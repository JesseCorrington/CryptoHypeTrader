console.log("starting client app");

var pending = 2
var chartData = []


function normalize(arr) {
    // y = (x - min) / (max - min)
    min = 100000000
    max = -1000000000
    for (var i = 0; i < arr.length; i++) {
        var x = arr[i][1]
        if (x < min) min = x;
        if (x > max) max = x;
    }

    for (var i = 0; i < arr.length; i++) {
        var x = arr[i][1]
        arr[i][1] = (x - min) / (max - min)
    }
}


function buildCompareChart() {
    Highcharts.stockChart('container', {

        yAxis: [{
            labels: {
                align: 'right',
                x: -3
            },
            title: {
                text: 'Close Price'
            },
            height: '60%',
            lineWidth: 2,
            resize: {
                enabled: true
            }
        }, {
            labels: {
                align: 'right',
                x: -3
            },
            title: {
                text: 'Reddit Growth'
            },
            top: '65%',
            height: '35%',
            offset: 0,
            lineWidth: 2
        }
        ],

        rangeSelector: {
            selected: 4
        },

        plotOptions: {
            series: {
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


function get_stats(coinId, symbol) {
    var url = '/api/historical_social_stats?coin_id=' + coinId;

    $.getJSON(url, function (data) {
        var series = data;

        var growth = [series[0][0], 0]
        for (var i = 1; i < series.length; i++) {
            var n = [series[i][0], series[i][1] - series[i - 1][1]]

            //n[1] *= 1000000

            if (n[1] <= 0)
                n[1] = 1

            console.log(`${new Date(n[0])}, ${n[1]}`)

            growth.push(n)
        }

        normalize(series);

        chartData.push({
            name: symbol + " reddit subs",
            yAxis: 0,
            data: series
        });

                var groupingUnits = [[
            'week',                         // unit name
            [1]                             // allowed multiples
        ], [
            'month',
            [1, 2, 3, 4, 6]
        ]]

        chartData.push({
            type: 'column',
            name: 'Volume',
            data: growth,
            yAxis: 1,
            dataGrouping: {
                units: groupingUnits
            }
        });

        pending--;
        if (pending == 0) {
            buildCompareChart()
        }
    });
}


function get_prices(coinId, symbol) {
    var url = '/api/historical_prices?coin_id=' + coinId;

    $.getJSON(url, function (data) {
        series = data;

        volume = []
        for (var i = 0; i < series.length; i++) {
            var v = series[i][2]
            if (v == null)
                v = 0;

            v = 100;

            volume.push([series[i][0], v])
        }

        normalize(series);
        chartData.push({
            name: symbol + " price",
            yAxis: 0,
            data: series
        });

        var groupingUnits = [[
            'week',                         // unit name
            [1]                             // allowed multiples
        ], [
            'month',
            [1, 2, 3, 4, 6]
        ]]

        /*chartData.push({
            type: 'column',
            name: 'Volume',
            data: volume,
            yAxis: 1,
            //dataGrouping: {
            //    units: groupingUnits
            //}
        });*/

        pending--;
        if (pending == 0) {
            buildCompareChart()
        }
    });
}

var coins = undefined

function get_coins() {
    var url = '/api/coins';
    $.getJSON(url, function (data) {
        coins = data;

        setSymbol("BTC");
    });
}


function setSymbol(symbol) {
    if (!symbol) {
        symbol = $("#symbol").val();
    }

    pending = 2
    chartData = []

    // TODO: make a by symbol map, and deal with duplicate symbols too
    var coin_id = undefined;
    for (var i = 0; i < coins.length; i++) {
        if (symbol === coins[i].symbol) {
            coin_id = coins[i]._id;
            break;
        }
    }


    get_prices(coin_id, symbol);
    get_stats(coin_id, symbol);
}


get_coins();
