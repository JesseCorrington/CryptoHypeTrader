<template>
  <v-card flat>
    <v-card-title>
      <v-spacer></v-spacer><v-spacer></v-spacer>
      <v-text-field append-icon="search" label="Search" single-line hide-details v-model="search"></v-text-field>
    </v-card-title>

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

        <td :class="props.item.growth.price.d1_pct >= 0? 'green--text' : 'red--text'" align="right">{{ props.item.growth.price.d1_pct | percent}}</td>
        <td :class="props.item.growth.reddit.d1_pct >= 0? 'green--text' : 'red--text'" align="right">{{ props.item.growth.reddit.d1_pct | percent}}</td>
        <td :class="props.item.growth.twitter.d1_pct >= 0? 'green--text' : 'red--text'" align="right">{{ props.item.growth.twitter.d1_pct | percent}}</td>
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
      selected: undefined
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
    }
  }
};
</script>
