<template>
  <div>
    <h1>Coin Summaries</h1>
    <div v-if="coins.length > 0">
      <coin-summaries-table :items="coins" v-model="selected"/>
    </div>
    <div v-else>
      Loading coin summaries...
    </div>

      <v-select
        label="Select Coins"
        :items="coins"
        v-model="selected"
        item-text="name"
        item-value="symbol"
        key="symbol"
        multiple
        chips
        deletable-chips
        autocomplete
        return-object
      ></v-select>

    <coin-chart :coins="selected"/>

  </div>
</template>


<script>
import Services from '@/services/Services'
import Coin from '@/models/Coin'

export default {
  data () {
    return {
      coins: [],
      selected: []
    }
  },

  mounted () {
    this.getCoinSummaries()
  },

  methods: {
    async getCoinSummaries() {
      const response = await Services.getCoinSummaries();

      // TODO: maybe move this into the service?
      var cs = []
      response.data.forEach(function(coinData) {
        cs.push(new Coin(coinData))
      });

      this.coins = cs;
    },

    onSelection(newSelected) {
      this.selected = newSelected;
    }
  }
}
</script>
