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


var symbol = "NEO"

function get_stats(coinId, symbol) {
    var url = '/api/social_stats?where={"coin_id": ' + coinId + '}&sort=date'

    $.getJSON(url, function (data) {
        series = []

        for (var i = 1; i < data._items.length; i++) {
            var date = new Date(data._items[i].date).getTime()
            var subs = parseFloat(data._items[i].reddit_subscribers)
            var prevSubs = parseFloat(data._items[i - 1].reddit_subscribers)

            //growth = subs - prevSubs;
            //growth /= 1000

            series.push([date, subs])
        }

        normalize(series);
        chartData.push({
            name: symbol + " reddit subs",
            data: series
        });

        //buildSingleChart()

        pending--;
        if (pending == 0) {
            buildCompareChart()
        }
    });
}


function get_prices(coinId, symbol) {
    var url = '/api/prices?where={"coin_id": '+ coinId +'}&sort=date'

    $.getJSON(url, function (data) {
        series = []

        for (var i in data._items) {
            var date = new Date(data._items[i].date).getTime()
            var price = parseFloat(data._items[i].close)

            series.push([date, price])
        }

        normalize(series);
        chartData.push({
            name: symbol + " price",
            data: series
        });

        buildSingleChart();
        
        pending--;
        if (pending == 0) {
            buildCompareChart()
        }
    });
}


function get_coins() {
    var url = '/api/coins';
    $.getJSON(url, function (coins) {
        console.log(coins);

        coins = coins._items;

        btc = coins[0];

        get_stats(btc._id);
        get_prices(btc._id);
    });
}


get_coins();
