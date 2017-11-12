class RunningTaskTable extends Table {
    constructor(cointainer, width, height) {
        super(cointainer, width, height);

        super.setColumns([
            // TODO: we could set cols in the ctor
            {header: "Name", key: "name"},
            {header: "Symbol", key: "symbol"},
            {header: "Subreddit", key: "subreddit"}
        ]);
    }

    setData(stats) {
        super.setData(stats);
    }
}

$(document).ready(function () {
    coins = $.getJSON("/api/coins", function(coins) {
        table = new RunningTaskTable("coinsTable");


        for (var i = 0; i < coins.length; i++) {
            var sub = coins[i].subreddit;
            if (sub) {
                coins[i].subreddit = '<a href="https://www.reddit.com/r/' + sub + '">' + sub + '</a>';
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
