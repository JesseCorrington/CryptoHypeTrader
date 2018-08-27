<template>
<div>
    <v-toolbar app fixed clipped-left>
        <v-toolbar-title align="center">Crypto Hype Trader</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items class="hidden-sm-and-down">
            <v-btn flat @click="showCoins"><v-icon>view_list</v-icon>Coins</v-btn>
            <v-btn flat @click="showCharts"><v-icon>show_chart</v-icon>Charts</v-btn>
            <v-btn flat @click="showAdmin"><v-icon>assessment</v-icon>Admin</v-btn>
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
    </v-content>

    <v-footer app fixed>
        <span>&copy; 2018  | about | contact</span>
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
        coins: []
    }),

    props: {
        source: String
    },

    mounted () {
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

        addCoinSummaries(coinSummaries) {
            for (var i = 0; i < coinSummaries.length; i++) {
                this.coins.push(new Coin(coinSummaries[i]));
            }
        },

        async getCoinSummaries() {
            // TODO: this could be optimized by just loading the coin names list initially
            // which would allow populating search lists, and then on demand we can load
            // the full coin summaries. For now this is simple and good enough

            const initial = await Services.getCoinSummaries(1, 10);
            this.addCoinSummaries(initial.data);

            const remainder = await Services.getCoinSummaries(11, 2000);
            this.addCoinSummaries(remainder.data);
        },
    }
}
</script>


<style>
    .ntp {
        margin-top: -8.5%;
    }
</style>
