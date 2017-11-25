"use strict"


class Coin {
    constructor(data) {
        for (var key in data) {
            this[key] = data[key]
        }
    }

    _makeUrl(base, key) {
        if (this[key]) {
            return base + this[key]
        }

        return ""
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
}

Vue.use(Vuetify)


var app = new Vue({
  el: '#vueApp',
  data: {
      headers: [
          {text: 'Name', value: 'name', align: "left"},
          {text: 'Symbol', value: 'symbol'},
          {text: "Coinmarketcap", value: "cmc_id"},
          {text: "CryptoCompare", value: "cc_id"},
          {text: "Subreddit", value: "subreddit"},
          {text: "Twitter", value: "twitter"},
          {text: "Bitcointalk-ANN", value: "btctalk_ann"},
          {text: "1d", value: "_1d_p"},
          {text: "3d", value: "_3d_p"},
          {text: "5d", value: "_5d_p"}
        ],
      items: [],
      selected: [],
      search: "",
      pagination: {
          sortBy: 'start_time'
      }
  },

  mounted: function() {
      var self = this
      $.getJSON('/api/coins', function (json) {
          self.items = json;
      });
  }
});