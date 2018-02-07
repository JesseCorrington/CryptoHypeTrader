"use strict"

class Coin {
    constructor(data) {
        for (var key in data) {
            this[key] = data[key]
        }

        this.timeSeries = {}
        this.seriesLoaded = false;
        this.onChart = false
    }

    _makeUrl(base, key) {
        if (this[key]) {
            return '<a href="' + base + this[key] + '">' + this[key] + "</a>";
        }

        return ""
    }

    loadTimeSeries() {
        var self = this;

        $.getJSON('/api/prices?coin_id=' + this.coin_id, function (data) {
            self.timeSeries.prices = data;
            addSeriesToChart(self.symbol + " Price", data);
        });

        $.getJSON('/api/reddit_stats?coin_id=' + this.coin_id, function (data) {
            self.timeSeries.reddit_stats = data;
            addSeriesToChart(self.symbol + "Reddit Subs", data);
        });

        $.getJSON('/api/twitter_counts?coin_id=' + this.coin_id, function (data) {
            self.timeSeries.twitter_counts = data;
            addSeriesToChart(self.symbol + "Twitter Counts", data);
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

var coins = []

Vue.use(Vuetify)

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
      }
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

    // TODO: this is doing normalize in place, so won't allow turning on/off via UI
    normalize(series);

    chart.addSeries({
        id: 0,
        name: name,
        data: series
    });
}


function buildChart() {
    chart = Highcharts.stockChart('priceChart', {
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
        }
    });
}

