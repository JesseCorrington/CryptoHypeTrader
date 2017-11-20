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
            {header: "1d", key: "1d_p"},
            {header: "3d", key: "3d_p"},
            {header: "5d", key: "5d_p"},
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


$(document).ready(function () {
    coins = $.getJSON("/api/coins", function(coins) {
        var table = new RunningTaskTable("coinsTable");

        for (var i = 0; i < coins.length; i++) {
            var coin = new Coin(coins[i])

            function link(url, name) {
                if (url && name) {
                    return `<a href="${url}">${name}</a>`
                }
                return ""
            }

            coins[i].subreddit = link(coin.subredditUrl(), coin.subreddit)
            coins[i].twitter = link(coin.twitterUrl(), coin.twitter)
            coins[i].btctalk_ann = link(coin.bitcointalkUrl(), coin.btctalk_ann)
            coins[i].cmc_id = link(coin.coinmarketcapUrl(), coin.cmc_id)
        }

        table.setData(coins);
    });
});
