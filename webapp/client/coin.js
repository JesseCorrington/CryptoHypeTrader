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
        series = data;
        normalize(series);

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


function get_prices(coinId, symbol) {
    var url = '/api/historical_prices?coin_id=' + coinId;

    $.getJSON(url, function (data) {
        series = data;

        normalize(series);
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

    get_stats(coin_id, symbol);
    get_prices(coin_id, symbol);
}


get_coins();
