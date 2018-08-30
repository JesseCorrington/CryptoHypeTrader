import Api from '@/services/Api'

export default {
    getCoins() {
        return Api().get('coins');
    },

    getCoin(params) {
  	    return Api().get('coin/' + params.id);
    },

    getCoinSummaries(start, limit) {
  	    return Api().get('coin_summaries', {
  	        "params": {
  	            "start": start,
                "limit": limit
            }
        });
    },

    getCoinPrices(coinId) {
  	    return Api().get('prices/' + coinId);
    },

    getRedditStats(coinId) {
        return Api().get('reddit_stats/' + coinId);
    },

    getRedditComments(coinId) {
        return Api().get('reddit_comments/' + coinId);
    },

    getTwitterComments(coinId) {
        return Api().get('twitter_comments/' + coinId);
    },

    getRecentComments() {
        return Api().get('recent_comments');
    },

    getIngestionTasks(name) {
        if (name === undefined)
            return Api().get('ingestion_tasks');
        else {
            return Api().get('ingestion_tasks/' + name);
        }
    },

    getDBStats() {
        return Api().get('db_stats');
    },

    cancelIngestionTask(id) {
        return Api.get('ingestion_tasks/cancel/' + id);
    }
}
