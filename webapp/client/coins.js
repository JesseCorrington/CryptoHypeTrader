class RunningTaskTable extends Table {
    constructor(cointainer, width, height) {
        super(cointainer, width, height);

        super.setColumns([
            // TODO: we could set cols in the ctor
            {header: "Name", key: "name"},
            {header: "Symbol", key: "symbol"},
            {header: "Coinmarketcap", key: "cmc_id"},
            {header: "CryptoCompare", key: "cc_id"},
            {header: "Subreddit", key: "subreddit"},
            {header: "Twitter", key: "twitter"},
            {header: "Bitcointalk ANN", key: "btctalk_ann"},
        ]);
    }

    setData(stats) {
        super.setData(stats);
    }
}

class Coin {
    constructor(data) {
        for (var key in data) {
            this[key] = data[key]
        }
    }

    subredditUrl() {
        if (this.subreddit)
            return "https://www.reddit.com/r/" + this.subreddit;

        return "";
    }

    twitterUrl() {
        if (this.twitter)
            return "https://www.twitter.com/" + this.twitter;

        return "";
    }

    bitcointalkUrl() {
        if (this.btctalk_ann)
            return "https://www.bitcointalk.org/?topic=" + this.btctalk_ann;

        return "";
    }
}


$(document).ready(function () {
    coins = $.getJSON("/api/coins", function(coins) {
        table = new RunningTaskTable("coinsTable");


        for (var i = 0; i < coins.length; i++) {
            var sub = coins[i].subreddit;
            var twitter = coins[1].twitter;

            coin = new Coin(coins[i])

            if (sub) {
                coins[i].subreddit = `<a href="${coin.subredditUrl()}">${coin.subreddit}</a>`
                coins[i].twitter = `<a href="${coin.twitterUrl()}">${coin.twitter}</a>`
                coins[i].btctalk_ann = `<a href="${coin.bitcointalkUrl()}">${coin.btctalk_ann}</a>`
            }
        }

        table.setData(coins);

        // TODO: we want to add some stats here too
        // market cap, price, 24 hr volume, 24hr price change,
        // 3 day price change, 24hr reddit sub change, 3 day reddit sub change, etc.

        // TODO: we need some kind of get summary end point for all this data,
        // or maybe just have coins always give it for now

    });
});
