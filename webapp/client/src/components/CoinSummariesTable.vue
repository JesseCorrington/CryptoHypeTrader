<template>
  <v-card flat>
      <v-toolbar>
          <v-text-field append-icon="search" label="Search" single-line hide-details v-model="search"></v-text-field>
          <v-spacer></v-spacer>
          <v-btn-toggle v-model="selectedTimeInterval" mandatory>
              <v-toolbar-items v-for="interval in timeIntervals">
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
  </v-card>
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
          {disp: '2h', key: "h2_pct"},
          {disp: '6h', key: "h6_pct"},
          {disp: '12h', key: "h12_pct"},
          {disp: '1d', key: "d1_pct"},
          {disp: '3d', key: "d3_pct"},
          {disp: '5d', key: "d5_pct"},
          {disp: '7d', key: "d7_pct"},
      ],
      selectedTimeInterval: 3,
      di: "d1_pct"
    }
  },

  mounted () {
    this.selected = this.value;
  },

  watch: {
    value: function() {
      this.selected = this.value;
    },

    selected: function() {
      this.$emit('input', this.selected)
    },

    selectedTimeInterval: function(val) {
        this.di = this.timeIntervals[this.selectedTimeInterval].key;

        this.headers[4].text = `${this.di} Price`
        this.headers[4].value = `growth.price.${this.di}`

        this.headers[5].text = `${this.di} Reddit`
        this.headers[5].value = `growth.reddit.${this.di}`

        this.headers[6].text = `${this.di} Twitter`
        this.headers[6].value = `growth.twitter.${this.di}`
    }
  }
};
</script>
