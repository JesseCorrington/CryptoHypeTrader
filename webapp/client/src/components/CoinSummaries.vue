<template>
  <div>
    <div v-if="coins.length > 0">
      <coin-summaries-table :items="coins" v-model="selected"/>
    </div>
    <div v-else>
      Loading coin summaries...
    </div>
  </div>
</template>


<script>
export default {
  data () {
    return {
      selected: []
    }
  },

  props: ['coins'],

  methods: {
    onSelection(newSelected) {
      this.selected = newSelected;
    }
  }
}
</script>
