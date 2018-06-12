import Services from '@/services/Services'

export default class Coin {
    constructor(data) {
        for (var key in data) {
            this[key] = data[key]

            if (this[key] === null)
                this[key] = 0
        }

        // TODO: should the serer set this??

        // TODO: don't specify full domain??
        this.iconUrl = `http://cryptohypetrader.com/static/icons/icon${this.coin_id}.png`
        this.subredditUrl = `https://www.reddit.com/r/${this.subreddit}`
        this.twitterUrl = `https://www.twitter.com/${this.subreddit}`

        this.timeSeries = {};
        this.comments = [];
        this.seriesLoaded = false;
        this.onChart = false;
    }

    _makeUrl(base, key, namePrefix) {
        if (this[key]) {
            return '<a href="' + base + this[key] + '">' + namePrefix + this[key] + "</a>";
        }

        return "";
    }

    splitSeries(data, names) {
        var split = {};

        names.forEach(name => {
            split[name] = [];
        });

        data.forEach(entry => {
            var time = entry[0]

            for (var i = 0; i < names.length; i++) {
                var val = entry[i + 1];
                split[names[i]].push([time, val]);
            }
        });

        return split;
    }

    seriesGrowth(series) {
        // Convert to 24hr growth

        var subs = series["subs"];
        var growth = [[subs[0][0], 0]]

        for (var i = 1; i < subs.length; i++) {
            growth.push([subs[i][0], subs[i][1] - subs[i - 1][1]]);
        }

        return growth
    }

    async loadSeriesData(onSeriesLoaded) {
        // TODO: convert to promise.all, consider rolling into one API endpoint
        const response = await Services.getCoinPrices(this.coin_id);
        onSeriesLoaded("price", response.data)

        const r2 = await Services.getRedditStats(this.coin_id);
        var names = ["subs", "subs active"];
        var series = this.splitSeries(r2.data, names);
        series["subs growth"] = this.seriesGrowth(series);
        for (var name in series) {
            onSeriesLoaded("reddit " + name, series[name]);
        }

        const r3 = await Services.getRedditComments(this.coin_id);
        var names = ["avg sentiment", "post count", "strong pos", "strong neg", "avg score", "sum score"];
        var series = this.splitSeries(r3.data, names);
        for (var name in series) {
            onSeriesLoaded("reddit " + name, series[name]);
        }

        const r4 = await Services.getTwitterComments(this.coin_id);
        var names = ["avg sentiment", "post count", "strong pos", "strong neg", "avg score", "sum score"];
        var series = this.splitSeries(r4.data, names);
        for (var name in series) {
            onSeriesLoaded("twitter " + name, series[name]);
        }

        this.seriesLoaded = true;
        this.onChart = true;
    }

    async loadComments() {
        const req = await Services.getRecentComments("reddit", this.coin_id);
        this.comments = req.data;
    }

    detailLink() {
        return '<a href ="coin.html?id=' + this.coin_id + '">' + this.name + '</a>';
    }

    subredditUrl() {
        return this._makeUrl("https://www.reddit.com/r/", "subreddit", "r/");
    }

    twitterUrl() {
        return this._makeUrl("https://www.twitter.com/", "twitter", "@");
    }
}

Coin.prototype.toString = function() {
    return this.name;
};
