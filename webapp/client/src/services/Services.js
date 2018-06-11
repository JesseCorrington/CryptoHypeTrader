import Api from '@/services/Api'

export default {
  getCoins() {
    return Api().get('coins')
  },

  getCoin(params) {
  	return Api().get('coin/' + params.id)
  },

  getCoinSummaries() {
  	return Api().get('coin_summaries')
  },

  getCoinPrices(coinId) {
  	return Api().get('prices/' + coinId)
  },

  getRedditStats(coinId) {
    return Api().get('reddit_stats/' + coinId)
  },

  getRedditComments(coinId) {
    return Api().get('reddit_comments/' + coinId)
  },

  getTwitterComments(coinId) {
    return Api().get('twitter_comments/' + coinId)
  },

  getRecentComments(coinId) {
    return Api().get('recent_comments/' + coinId)
  }
}
