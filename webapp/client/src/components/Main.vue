<template>
<div>
    <v-toolbar app fixed clipped-left dark color="primary">
        <v-toolbar-title align="center">Crypto Hype Trader</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items class="hidden-sm-and-down">
            <v-btn flat @click="showCoins"><v-icon>view_list</v-icon>Coins</v-btn>
            <v-btn flat @click="showCharts"><v-icon>show_chart</v-icon>Charts</v-btn>
            <v-btn flat @click="showComments"><v-icon>comment</v-icon>Comments</v-btn>
            <v-btn v-if="devMode==true" flat @click="showAdmin"><v-icon>assessment</v-icon>Admin</v-btn>
        </v-toolbar-items>
    </v-toolbar>

    <v-content class="ntp">
        <div v-if="view==='coins'">
            <coin-summaries :coins="coins"/>
        </div>
        <div v-else-if="view==='charts'">
            <coin-chart :coins="coins"/>
        </div>
        <div v-else-if="view==='admin'">
            <admin/>
        </div>
        <div v-else-if="view==='comments'">
            <comments-table :coins="coins"/>
        </div>
    </v-content>

    <v-footer app fixed dark color="secondary">
        <span>
            &copy; 2018 &ensp; | &ensp;
            <strong>Updated:</strong> {{lastPriceUpdate  |  dateTime}} &ensp; | &ensp; <strong>Total Data Points:</strong> {{totalDataPoints | number}}
            &ensp; | &ensp; <a target=”_blank” href="https://github.com/JesseCorrington/CryptoHypeTrader">GitHub Source</a>
        </span>
    </v-footer>
</div>
</template>


<script>
import Services from '@/services/Services'
import Coin from '@/models/Coin'

export default {
    data: () => ({
        drawer: true,
        view: "coins",
        coins: [],
        lastPriceUpdate: undefined,
        totalDataPoints: undefined,
        devMode: false,
        highestCoinId: 0
    }),

    props: {
        source: String
    },

    mounted () {
        this.devMode = this.$route.query.dev === "true";

        this.getCoinSummaries();
    },

    methods: {
        showCoins() {
            this.view = "coins";
        },

        showCharts() {
            this.view = "charts";
        },

        showAdmin() {
            this.view = "admin";
        },

        showComments() {
            this.view = "comments";
        },

        addCoinSummaries(coinSummaries) {
            for (var i = 0; i < coinSummaries.length; i++) {
                var coinId = coinSummaries[i].coin_id;
                if (coinId > this.highestCoinId) {
                    this.highestCoinId = coinId;
                }

                this.coins.push(new Coin(coinSummaries[i]));
            }
        },

        async getCoinSummaries() {
            // TODO: this could be optimized by just loading the coin names list initially
            // which would allow populating search lists, and then on demand we can load
            // the full coin summaries. For now this is simple and good enough

            const initial = await Services.getCoinSummaries(1, 20);
            this.addCoinSummaries(initial.data);

            // Mark the 10 coins that were added last
            for (var i = 0; i < this.coins.length; i++) {
                this.coins[i].recentlyAdded = this.coins[i].coin_id > this.highestCoinId - 10;
            }

            const dbStats = await Services.getDBStats();
            this.lastPriceUpdate = new Date(dbStats.data.last_price_update);
            this.totalDataPoints = dbStats.data.total_data_points;

            // Landing page is up, now fetch the rest of the coins
            const remainder = await Services.getCoinSummaries(21, 2000);
            this.addCoinSummaries(remainder.data);
        }
    }
}
</script>


<style scoped>
    .ntp {
        margin-top: -8.5%;
    }
</style>
