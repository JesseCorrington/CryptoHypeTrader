"use strict"


class Coin {
    constructor(data) {
        for (var key in data) {
            this[key] = data[key]
        }
    }

    _makeUrl(base, key) {
        if (this[key]) {
            return base + this[key]
        }

        return ""
    }


    subredditUrl() {
        return this._makeUrl("https://www.reddit.com/r/", "subreddit");
    }

    twitterUrl() {
        return this._makeUrl("https://www.twitter.com/", "twitter");
    }

    bitcointalkUrl() {
        return this._makeUrl("https://www.bitcointalk.org/?topic=", "btctalk_ann");
    }

    coinmarketcapUrl() {
        return this._makeUrl("https://coinmarketcap.com/currencies/", "cmc_id");
    }
}

Vue.use(Vuetify)

Vue.component('price-chart', {
  template: '<h1>Price Chart</h1><div id="priceChart"></div>'
});

function foo() {
    console.log("Tab clicked")
}


var app = new Vue({
  el: '#vueApp',
  data: {
      headers: [
          {text: 'Name', value: 'name', align: "left"},
          {text: 'Symbol', value: 'symbol'},
          {text: 'Price', value: 'price'},
          {text: 'Market Cap', value: 'market_cap'},

          {text: "Reddit h2", value: "growth.reddit.h2"},
          {text: "Reddit h2_pct", value: "growth.reddit.h2_pct"},
          {text: "Reddit h6", value: "growth.reddit.h6"},
          {text: "Reddit h6_pct", value: "growth.reddit.h6_pct"},
          {text: "Reddit d1", value: "growth.reddit.d1"},
          {text: "Reddit d1_pct", value: "growth.reddit.d1_pct"},
          {text: "Reddit d3", value: "growth.reddit.d3"},
          {text: "Reddit d3_pct", value: "growth.reddit.d3_pct"},
          {text: "Reddit d5", value: "growth.reddit.d5"},
          {text: "Reddit d5_pct", value: "growth.reddit.d5_pct"},

          {text: "Twitter d1", value: "growth.twitter.d1"},
          {text: "Twitter d1_pct", value: "growth.twitter.d1_pct"},
        ],
      items: [],
      selected: [],
      search: "",
      pagination: {
          sortBy: 'date'
      }
  },

  mounted: function() {
      var self = this
      $.getJSON('/api/coin_summaries', function (json) {
          json.forEach(function(coin) {
              for (var key in coin) {
                  if (coin[key] === null)
                      coin[key] = 0
              }

              // TODO: we should fix the server so we don't need this
              // since this table doesn't grow, we can just make each record full with 0s
              if (coin.growth === undefined)
                  coin.growth = {}

              if (coin.growth.twitter === undefined)
                  coin.growth.twitter = {}

              if (coin.growth.reddit === undefined) {
                  coin.growth.reddit = {
                      "h2": 0,
                      "h6": 0,
                      "d1": 0,
                      "d2": 0,
                      "d3": 0,
                      "d4": 0,
                      "d5": 0,
                      "d6": 0,
                      "h2_pct": 0,
                      "h6_pct": 0,
                      "d1_pct": 0,
                      "d2_pct": 0,
                      "d3_pct": 0,
                      "d4_pct": 0,
                      "d5_pct": 0,
                      "d6_pct": 0
                  }
              }
          });

          self.items = json;
      });
  },
    methods: {
        tabClicked: function () {
            console.log("clicked tab");
            var coin = this.selected[0];
            var pending = 2
            var chartData = []

            get_prices(coin.coin_id, coin.symbol);
            get_stats(coin.coin_id, coin.symbol);
        }
    }
});



var pending = 2
var chartData = []


function normalize(arr) {
    // y = (x - min) / (max - min)
    var min = 100000000
    var max = -1000000000
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
    Highcharts.stockChart('priceChart', {

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
        var series = data;

        var volume = [];
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
