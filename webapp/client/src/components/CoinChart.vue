<template>
  <div>
    <v-select
      label="Select Features"
      :items="chartFeatures"
      v-model="selectedChartFeatures"
      multiple
      chips
      deletable-chips
      autocomplete
    ></v-select>

    <div ref="stockChart"></div>
  </div>
</template>


<script>
import Services from '@/services/Services'
import Highcharts from 'highcharts'

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

// TODO: prob visible features is a better name
var visibleSeries = {"price": true};

function arrayDiff(a, b) {
    return a.filter(function(i) {return b.indexOf(i) < 0;});
}

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

export default {
  props: ['coins'],

  data() {
    return {
      prevCoins: [],
      chartFeatures: CHART_FEATURES,
      selectedChartFeatures: ["Price"],
      prevSelectedChartFeatures: ["Price"]
    }
  },

  mounted () {
    this.chart = Highcharts.stockChart(this.$refs.stockChart, {
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
  },

  methods: {
    addSeriesToChart(symbol, name, series) {
      if (!visibleSeries[name.toLowerCase()]) {
          return;
      }

      if (this.chart.get(name)) {
          // Prevent adding duplicates
          return;
      }

      // TODO: this is doing normalize in place, so won't allow turning on/off via UI
      //normalize(series);

      this.chart.addSeries({
          id: symbol.toLowerCase() + " " + name.toLowerCase(),
          name: symbol + " " + name,
          data: series
      });
    },

    removeSeriesFromChart(symbol, name) {
        var series = this.chart.get(symbol.toLowerCase() + " " + name.toLowerCase());
        if (series) {
          series.remove();
        }
    }
  },

  watch: {
    coins: function() {
      console.log("selected coins changed");

      var removed = arrayDiff(this.prevCoins, this.coins);
      var added = arrayDiff(this.coins, this.prevCoins);
      this.prevCoins = this.coins;

      var self = this;

      // load data if not cached, and display
      added.forEach(coin => {
        if (!coin.onChart && !coin.seriesLoaded) {
          coin.loadData(function(name, data) {
            coin.timeSeries[name] = data; // TODO: caching should happen in coin class
            self.addSeriesToChart(coin.symbol, name, data);
          });
        }
        else if (!coin.onChart) {
          for (var name in coin.timeSeries) {
            this.addSeriesToChart(coin.symbol, name, coin.timeSeries[name]);
          }
        }
      });

      // hide deselected coin time series
      removed.forEach(coin => {
        for (var name in coin.timeSeries) {
          this.removeSeriesFromChart(coin.symbol, name);
        }
        coin.onChart = false;
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

      this.coins.forEach(coin => {
          deselected.forEach(feature => {
              this.removeSeriesFromChart(coin.symbol, feature);
          });

          selected.forEach(feature => {
              var seriesKey = feature.toLowerCase();
              var series = coin.timeSeries[seriesKey];
              this.addSeriesToChart(coin.symbol, feature, series);
          });
      });
    }
  }
}
</script>


<style scoped>
.stock {
  width: 70%;
  margin: 0 auto
}

#nav ul {
    float: right;
    list-style: none;
    padding: 0;
    margin:0 [B]61px[/B] 0 0;
}
</style>
