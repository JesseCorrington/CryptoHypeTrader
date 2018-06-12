<template>
  <div>
      <v-select
          label="Select Coins"
          :items="coins"
          v-model="selectedCoins"
          item-text="name"
          item-value="symbol"
          key="symbol"
          multiple
          chips
          deletable-chips
          autocomplete
          return-object
      >
          <template slot="item" slot-scope="data">
              <v-list-tile-avatar>
                  <img :src="data.item.iconUrl"/>
              </v-list-tile-avatar>
              <v-list-tile-content>
                  <v-list-tile-title>{{data.item.name}} ({{data.item.symbol}})</v-list-tile-title>
              </v-list-tile-content>
          </template>

          <template slot="selection" slot-scope="data">
              <v-chip
                  close
                  @input="data.parent.selectItem(data.item)"
                  :selected="data.selected"
                  class="chip--select-multi"
                  :key="data.item.coin_id"
              >
                  <v-avatar>
                      <img :src="data.item.iconUrl">
                  </v-avatar>
                  {{ data.item.name }}
              </v-chip>
          </template>
      </v-select>

    <v-select
      label="Select Features"
      :items="chartFeatures"
      v-model="selectedChartFeatures"
      multiple
      chips
      deletable-chips
      autocomplete
    ></v-select>
    <v-checkbox label="Normalize" v-model="normalize"></v-checkbox>
    <div ref="stockChart"></div>
  </div>
</template>


<script>
import Services from '@/services/Services'
import Highcharts from 'highcharts'

const CHART_FEATURES = [
    "Price",
    "Volume",
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

function normalizeSeries(arr) {
    var norm = []

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
        norm[i] = [arr[i][0], (x - min) / (max - min)]
    }

    return norm;
}

export default {
  props: ['coins'],

  data() {
    return {
      prevCoins: [],
      selectedCoins: [],
      chartFeatures: CHART_FEATURES,
      selectedChartFeatures: ["Price"],
      prevSelectedChartFeatures: ["Price"],
      normalize: false
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

      var seriesNorm = normalizeSeries(series);

      this.chart.addSeries({
          id: symbol.toLowerCase() + " " + name.toLowerCase(),
          name: symbol + " " + name,
          data: this.normalize? seriesNorm : series,
          dataOrig: series,
          dataNorm: seriesNorm
      });
    },

    // TODO: symbol is not a unique id, use coin_id instead
    removeSeriesFromChart(symbol, name) {
        var series = this.chart.get(symbol.toLowerCase() + " " + name.toLowerCase());
        if (series) {
          series.remove();
        }
    }
  },

  watch: {
    selectedCoins: function() {
      console.log("selected coins changed");

      var removed = arrayDiff(this.prevCoins, this.selectedCoins);
      var added = arrayDiff(this.selectedCoins, this.prevCoins);
      this.prevCoins = this.selectedCoins;

      var self = this;

      // load data if not cached, and display
      added.forEach(coin => {
        if (!coin.onChart && !coin.seriesLoaded) {
          coin.loadSeriesData(function(name, data) {
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

      this.selectedCoins.forEach(coin => {
          deselected.forEach(feature => {
              this.removeSeriesFromChart(coin.symbol, feature);
          });

          selected.forEach(feature => {
              var seriesKey = feature.toLowerCase();
              var series = coin.timeSeries[seriesKey];
              this.addSeriesToChart(coin.symbol, feature, series);
          });
      });
    },

    normalize: function() {
        var dataKey = this.normalize === true? "dataNorm" : "dataOrig";
        for (var i = 0; i < this.chart.series.length; i++) {
            this.chart.series[i].setData(this.chart.series[i].options[dataKey], true, undefined, false);
        }
    }
  }
}
</script>
