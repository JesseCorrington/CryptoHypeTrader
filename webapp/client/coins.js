"use strict"

const CHART_FEATURES = [
    "Price",
    "Reddit Subs",
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

var visibleSeries = {"price": true};

function arrayDiff(a, b) {
    return a.filter(function(i) {return b.indexOf(i) < 0;});
}

class Coin {
    constructor(data) {
        for (var key in data) {
            this[key] = data[key]

            if (this[key] === null)
                this[key] = 0
        }

        this.timeSeries = {};
        this.comments = [];
        this.seriesLoaded = false;
        this.onChart = false;
    }

    _makeUrl(base, key, namePrefix) {
        if (this[key]) {
            return '<a href="' + base + this[key] + '">' + namePrefix + this[key] + "</a>";
        }

        return "";
    }

    showLoadedSeries() {
        for (var name in this.timeSeries) {
            addSeriesToChart(this.symbol, name, this.timeSeries[name]);
        }
    }

    hideLoadedSeries() {
        for (var name in this.timeSeries) {
            removeSeriesFromChart(this.symbol, name);
        }
        this.onChart = false;
    }

    onSeriesLoaded(name, data) {
        this.timeSeries[name] = data;
        addSeriesToChart(this.symbol, name, data);
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

    seriesGrowth(series) {
        // Convert to 24hr growth

        var subs = series["subs"];
        var growth = [[subs[0][0], 0]]

        for (var i = 1; i < subs.length; i++) {
            growth.push([subs[i][0], subs[i][1] - subs[i - 1][1]]);
        }

        return growth
    }

    loadData() {
        var self = this;

        $.getJSON('/api/prices?coin_id=' + this.coin_id, function (data) {
            self.onSeriesLoaded("price", data)
        });

        $.getJSON('/api/reddit_stats?coin_id=' + this.coin_id, function (data) {
            var names = ["subs", "subs active"];
            var series = self.splitSeries(data, names);

            series["subs growth"] = self.seriesGrowth(series);

            for (var name in series) {
                self.onSeriesLoaded("reddit " + name, series[name]);
            }
        });

        $.getJSON('/api/reddit_comments?coin_id=' + this.coin_id, function (data) {
            var names = ["avg sentiment", "post count", "strong pos", "strong neg", "avg score", "sum score"];

            var series = self.splitSeries(data, names);
            for (var name in series) {
                self.onSeriesLoaded("reddit " + name, series[name]);
            }
        });

        $.getJSON('/api/twitter_comments?coin_id=' + this.coin_id, function (data) {
            var names = ["avg sentiment", "post count", "strong pos", "strong neg", "avg score", "sum score"];

            var series = self.splitSeries(data, names);
            for (var name in series) {
                self.onSeriesLoaded("twitter " + name, series[name]);
            }
        });

        $.getJSON('/api/recent_comments?coin_id=' + this.coin_id, data => {
            self.comments = data;
        });

        this.seriesLoaded = true;
        this.onChart = true;
    }

    detailLink() {
        return '<a href ="coin.html?id=' + this.coin_id + '">' + this.name + '</a>';
    }

    subredditUrl() {
        return this._makeUrl("https://www.reddit.com/r/", "subreddit", "r/");
    }

    twitterUrl() {
        return this._makeUrl("https://www.twitter.com/", "twitter", "@");
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
          {text: 'Symbol', value: 'symbol', align: "left"},
          {text: 'Price', value: 'price', align: "right"},
          {text: 'Market Cap', value: 'market_cap', align: "right"},
          {text: '24hr', value: 'growth.price.d1_pct', align: "right"},
          {text: 'Reddit', value: 'subredditUrl()', align: "left"},
          {text: 'Twitter', value: 'twitterUrl()', align: "left"},
          {text: "Volume h6", value: "growth.volume.h6", align: "right"},
          {text: "Reddit h6", value: "growth.reddit.h6", align: "right"},
          {text: "Reddit h6_pct", value: "growth.reddit.h6_pct", align: "right"},
          {text: "Reddit d1", value: "growth.reddit.d1", align: "right"},
          {text: "Reddit d1_pct", value: "growth.reddit.d1_pct", align: "right"},
          {text: "Reddit d3", value: "growth.reddit.d3", align: "right"},
          {text: "Reddit d3_pct", value: "growth.reddit.d3_pct", align: "right"},
          {text: "Reddit d5", value: "growth.reddit.d5", align: "right"},
          {text: "Reddit d5_pct", value: "growth.reddit.d5_pct", align: "right"},
          {text: "Twitter d1", value: "growth.twitter.d1", align: "right"},
          {text: "Twitter d1_pct", value: "growth.twitter.d1_pct", align: "right"},
          {text: "CryptoCompare d1", value: "growth.crypto_compare.d1", align: "right"},
          {text: "CryptoCompare d1_pct", value: "growth.crypto_compare.d1_pct", align: "right"},
        ],
      items: [],
      selected: [],
      prevSelected: [],
      search: "",
      pagination: {
          sortBy: 'market_cap',
          descending: true
      },
      chartFeatures: CHART_FEATURES,
      selectedChartFeatures: ["Price"],
      prevSelectedChartFeatures: ["Price"]
  },

  mounted: function() {
      var self = this
      $.getJSON('/api/coin_summaries', function (json) {
          json.forEach(function(coinData) {
              coins.push(new Coin(coinData))
          });

          self.items = coins;

          buildChart();
      });
  },

    watch: {
        selected: function() {
            var deselected = arrayDiff(this.prevSelected, this.selected);
            var selected = arrayDiff(this.selected, this.prevSelected);
            this.prevSelected = this.selected;

            selected.forEach(coin => {
                if (!coin.onChart && !coin.seriesLoaded) {
                    coin.loadData();
                }
                else if (!coin.onChart) {
                    coin.showLoadedSeries();
                }
            });

            deselected.forEach(coin => {
                coin.hideLoadedSeries();
            });
        },

        selectedChartFeatures: function() {
            var deselected = arrayDiff(this.prevSelectedChartFeatures, this.selectedChartFeatures);
            var selected = arrayDiff(this.selectedChartFeatures, this.prevSelectedChartFeatures);
            this.prevSelectedChartFeatures = this.selectedChartFeatures;

            visibleSeries = {};
            this.selectedChartFeatures.forEach(feature => {
                visibleSeries[feature.toLowerCase()] = true;
            });

            this.selected.forEach(coin => {
                deselected.forEach(feature => {
                    removeSeriesFromChart(coin.symbol, feature);
                });

                selected.forEach(feature => {
                    var seriesKey = feature.toLowerCase();
                    var series = coin.timeSeries[seriesKey];
                    addSeriesToChart(coin.symbol, feature, series);
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

function addSeriesToChart(symbol, name, series) {
    if (!visibleSeries[name.toLowerCase()]) {
        return;
    }

    if (chart.get(name)) {
        // Prevent adding duplicates
        return;
    }

    // TODO: this is doing normalize in place, so won't allow turning on/off via UI
    normalize(series);

    chart.addSeries({
        id: symbol.toLowerCase() + " " + name.toLowerCase(),
        name: symbol + " " + name,
        data: series
    });
}

function removeSeriesFromChart(symbol, name) {
    var series = chart.get(symbol.toLowerCase() + " " + name.toLowerCase());
    if (series) {
        series.remove();
    }
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
