<template>
  <div>
      <v-toolbar>
          <v-text-field append-icon="search" label="Search" single-line hide-details v-model="search"></v-text-field>
          <v-spacer></v-spacer>
          <v-btn-toggle v-model="selectedCurrency" mandatory>
              <v-toolbar-items>
                  <v-btn>USD</v-btn>
                  <v-btn>BTC</v-btn>
              </v-toolbar-items>
          </v-btn-toggle>
          <v-spacer></v-spacer>
          <v-btn-toggle v-model="showPercent">
              <v-toolbar-items>
                  <v-btn>%</v-btn>
              </v-toolbar-items>
          </v-btn-toggle>
          <v-btn-toggle v-model="selectedTimeInterval" mandatory>
              <v-toolbar-items v-for="interval in timeIntervals" :key="interval.key">
                  <v-btn :key="interval.key">{{interval.disp}}</v-btn>
              </v-toolbar-items>
          </v-btn-toggle>
      </v-toolbar>

    <v-data-table
      :headers="headers"
      :search="search"
      :pagination.sync="pagination"
      :items="items"
      :rows-per-page-items="[10,20,50,100]"
      v-model="selected"
      class="elevation-1"
      item-key="_id"
      select-all>

      <template slot="items" slot-scope="props">
        <td><v-checkbox primary hide-details v-model="props.selected"></v-checkbox></td>
        <td alight="left">
            <img align="left" :src="props.item.iconUrl" width="32"/>
            <router-link :to="{ name: 'CoinDetail', params: { id: props.item.coin_id, coin: props.item } }">{{ props.item.name }} </router-link>
            ({{ props.item.symbol }})
        </td>

        <td align="right">{{ props.item.market_cap | currency}}</td>
        <td align="right">{{ props.item.price | currency}}</td>
        <td align="right">{{ props.item.volume | currency}}</td>

        <td :class="props.item.growth.price[di] >= 0? 'green--text' : 'red--text'" align="right">{{ props.item.growth.price[di] | percent}}</td>
        <td :class="props.item.growth.reddit[di] >= 0? 'green--text' : 'red--text'" align="right">{{ props.item.growth.reddit[di] | percent}}</td>
        <td :class="props.item.growth.twitter[di] >= 0? 'green--text' : 'red--text'" align="right">{{ props.item.growth.twitter[di] | percent}}</td>
      </template>
    </v-data-table>
  </div>
</template>


<script>
export default {
  props: ['items', 'value'],

  data () {
    return {
      headers: [
          {text: 'Name', value: 'name', align: "left"},
          {text: 'Market Cap', value: 'market_cap', align: "right"},
          {text: 'Price', value: 'price', align: "right"},
          {text: 'Volume', value: 'volume', align: "right"},
          {text: '24hr price', value: 'growth.price.d1_pct', align: "right"},
          {text: '24hr reddit', value: 'growth.reddit.d1_pct', align: "right"},
          {text: '24hr twitter', value: 'growth.twitter.d1_pct', align: "right"},
        ],
      search: "",
      pagination: {
          sortBy: 'market_cap',
          descending: true
      },
      selected: undefined,
      timeIntervals: [
          {disp: '2h', key: "h2"},
          {disp: '6h', key: "h6"},
          {disp: '12h', key: "h12"},
          {disp: '1d', key: "d1"},
          {disp: '3d', key: "d3"},
          {disp: '5d', key: "d5"},
          {disp: '7d', key: "d7"},
      ],
      selectedTimeInterval: 3,
      di: "d1_pct",
      selectedCurrency: "USD",
      showPercent: 0
    }
  },

  methods: {
      updateGrowthCols() {
          var key = this.di;
          var disp = this.timeIntervals[this.selectedTimeInterval].disp

          this.headers[4].text = `${disp} Price`
          this.headers[4].value = `growth.price.${key}`

          this.headers[5].text = `${disp} Reddit`
          this.headers[5].value = `growth.reddit.${key}`

          this.headers[6].text = `${disp} Twitter`
          this.headers[6].value = `growth.twitter.${key}`
      }
  },

  computed: {
      growthStyle() {
          return this.showPercent === 0? "_pct" : ""
      }
  },

  mounted () {
    this.selected = this.value;
  },

  watch: {
    value() {
      this.selected = this.value;
    },

    selected() {
      this.$emit('input', this.selected)
    },

    showPercent(val) {
        console.log(val);
        console.log(this.showPercent);
    },

    selectedTimeInterval(val) {
        this.di = this.timeIntervals[this.selectedTimeInterval].key + this.growthStyle;
    },

    growthStyle() {
        this.di = this.timeIntervals[this.selectedTimeInterval].key + this.growthStyle;
    },

    di() {
        this.updateGrowthCols();
    },
  }
};
</script>
