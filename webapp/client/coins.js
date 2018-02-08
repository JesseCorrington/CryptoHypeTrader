"use strict"

const CHART_FEATURES = [
    "Price",
    "Reddit Subs Growth",
    "Reddit Subs Active",
    "Reddit Avg Sentiment",
    "Reddit Post Count",
    "Reddit Strong Pos",
    "Reddit Strong Neg",
    "Reddit Avg Score",
    "Reddit Sum Score",
    "Twitter Avg Sentiment",
    "Twitter Post Count",
    "Twitter Strong Pos",
    "Twitter Strong Neg",
    "Twitter Avg Score",
    "Twitter Sum Score",
];

function arrayDiff(a, b) {
    return a.filter(function(i) {return b.indexOf(i) < 0;});
};

class Coin {
    constructor(data) {
        for (var key in data) {
            this[key] = data[key]
        }

        this.timeSeries = {};
        this.seriesLoaded = false;
        this.onChart = false;
    }

    _makeUrl(base, key) {
        if (this[key]) {
            return '<a href="' + base + this[key] + '">' + this[key] + "</a>";
        }

        return "";
    }

    splitSeries(data, names) {
        var split = {};

        names.forEach(name => {
            split[name] = [];
        });

        data.forEach(entry => {
            var time = entry[0]

            for (var i = 0; i < names.length; i++) {
                var val = entry[i + 1];
                split[names[i]].push([time, val]);
            }
        });

        return split;
    }

    loadTimeSeries() {
        var self = this;

        $.getJSON('/api/prices?coin_id=' + this.coin_id, function (data) {
            self.timeSeries.price = data;
            addSeriesToChart(self.symbol + " Price", data);
        });

        $.getJSON('/api/reddit_stats?coin_id=' + this.coin_id, function (data) {
            var names = ["subs growth", "subs active"];
            var series = self.splitSeries(data, names);

            // convert subs to subs growth
            var subs = series["subs growth"];
            var growth = [[subs[0][0], 0]]

            for (var i = 1; i < subs.length; i++) {
                growth.push([subs[i][0], subs[i][1] - subs[i - 1][1]]);
            }

            series["subs growth"] = growth;

            for (var name in series) {
                var s = series[name];
                self.timeSeries["reddit " + name] = s;
            }
        });

        $.getJSON('/api/twitter_comments?coin_id=' + this.coin_id, function (data) {
            var names = ["avg sentiment", "post count", "strong pos", "strong neg", "avg score", "sum score"];

            var series = self.splitSeries(data, names);
            for (var name in series) {
                var s = series[name];
                self.timeSeries["twitter " + name] = s;
            }
        });

        $.getJSON('/api/reddit_comments?coin_id=' + this.coin_id, function (data) {
            var names = ["avg sentiment", "post count", "strong pos", "strong neg", "avg score", "sum score"];

            var series = self.splitSeries(data, names);
            for (var name in series) {
                var s = series[name];
                self.timeSeries["reddit " + name] = s;
            }
        });

        this.seriesLoaded = true;
        this.onChart = true;
    }

    detailLink() {
        return '<a href ="coin.html?id=' + this.coin_id + '">' + this.name + '</a>';
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

    cryptoCompareUrl() {
        return "TODO";
        //return this._makeUrl("https://www.cryptocompare.com/coins/" btc "/overview/USD", "cmc_id");
    }
}

Coin.prototype.toString = function() {
    return this.name;
};

var coins = [];

Vue.use(Vuetify);

Vue.component('price-chart', {
    template: '<h1>Price Chart</h1><div id="priceChart"></div>'
});



var app = new Vue({
  el: '#vueApp',
  data: {
      headers: [
          {text: 'Name', value: 'detailLink()', align: "left"},
          {text: 'Symbol', value: 'symbol'},
          {text: 'Price', value: 'price'},
          {text: 'Market Cap', value: 'market_cap'},
          {text: 'Reddit', value: 'subredditUrl()'},
          {text: 'Twitter', value: 'twitterUrl()'},
          {text: 'CMC', value: 'coinmarketcapUrl()'},
          {text: 'BTC Talk', value: 'bitcointalkUrl()'},
          {text: 'CC', value: 'cryptoCompareUrl()'},
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
          {text: "CryptoCompare d1", value: "growth.crypto_compare.d1"},
          {text: "CryptoCompare d1_pct", value: "growth.crypto_compare.d1_pct"},
        ],
      items: [],
      selected: [],
      search: "",
      pagination: {
          sortBy: 'date'
      },
      chartFeatures: CHART_FEATURES,
      selectedChartFeatures: ["Price"],
      prevSelectedChartFeatures: []
  },

  mounted: function() {
      var self = this
      $.getJSON('/api/coin_summaries', function (json) {
          json.forEach(function(coin) {
              for (var key in coin) {

                  // TODO: move this into Coin class
                  if (coin[key] === null)
                      coin[key] = 0
              }
              coins.push(new Coin(coin))
          });

          self.items = coins;

          buildChart();
      });
  },

    watch: {
        selected: function() {
            this.selected.forEach(coin => {
                if (!coin.onChart && !coin.seriesLoaded) {
                    coin.loadTimeSeries();
                }
            });
        },

        selectedChartFeatures: function() {
            var deselected = arrayDiff(this.prevSelectedChartFeatures, this.selectedChartFeatures);
            var selected = arrayDiff(this.selectedChartFeatures, this.prevSelectedChartFeatures);
            this.prevSelectedChartFeatures = this.selectedChartFeatures;

            // TODO: need to handle adding and removing selected coins too

            this.selected.forEach(coin => {
                removeSeriesFromChart(coin.symbol, deselected);

                selected.forEach(feature => {
                    var seriesKey = feature.toLowerCase();
                    var series = coin.timeSeries[seriesKey];

                    addSeriesToChart(coin.symbol + " " + feature, series);
                });
            });
        }
    }
});



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


var chart = undefined;
function addSeriesToChart(name, series) {
    if (chart.get(name)) {
        // Prevent adding duplicates
        return;
    }

    // TODO: this is doing normalize in place, so won't allow turning on/off via UI
    normalize(series);

    chart.addSeries({
        id: name,
        name: name,
        data: series
    });
}

function removeSeriesFromChart(symbol, names) {
    names.forEach(name => {
        var series = chart.get(symbol + " " + name);
        if (series) {
            series.remove();
        }
    });
}


function buildChart() {
    chart = Highcharts.stockChart('priceChart', {
        yAxis: {
            labels: {
                align: 'right',
                x: -3
            },
            lineWidth: 2,
            resize: {
                enabled: true
            }
        },

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
        }
    });
}
