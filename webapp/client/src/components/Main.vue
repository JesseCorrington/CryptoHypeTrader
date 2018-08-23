<template>
<div>
    <v-navigation-drawer clipped fixed v-model="drawer" app>
        <v-list dense>
            <v-list-tile @click="showCoins">
                <v-list-tile-action>
                    <v-icon>view_list</v-icon>
                </v-list-tile-action>
                <v-list-tile-content>
                    <v-list-tile-title>Coins</v-list-tile-title>
                </v-list-tile-content>
            </v-list-tile>
            <v-list-tile @click="">
                <v-list-tile-action>
                    <v-icon>whatshot</v-icon>
                </v-list-tile-action>
                <v-list-tile-content>
                    <v-list-tile-title>Popular</v-list-tile-title>
                </v-list-tile-content>
            </v-list-tile>
            <v-list-tile @click="showCharts">
                <v-list-tile-action>
                    <v-icon>show_chart</v-icon>
                </v-list-tile-action>
                <v-list-tile-content>
                    <v-list-tile-title>Charts</v-list-tile-title>
                </v-list-tile-content>
            </v-list-tile>
            <v-list-tile @click="">
                <v-list-tile-action>
                    <v-icon>settings</v-icon>
                </v-list-tile-action>
                <v-list-tile-content>
                    <v-list-tile-title>Settings</v-list-tile-title>
                </v-list-tile-content>
            </v-list-tile>
            <v-list-tile @click="showAdmin">
                <v-list-tile-action>
                    <v-icon>assessment</v-icon>
                </v-list-tile-action>
                <v-list-tile-content>
                    <v-list-tile-title>Admin</v-list-tile-title>
                </v-list-tile-content>
            </v-list-tile>
            <v-list-tile @click="">
                <v-list-tile-action>
                    <v-icon>lock_open</v-icon>
                </v-list-tile-action>
                <v-list-tile-content>
                    <v-list-tile-title>Log In</v-list-tile-title>
                </v-list-tile-content>
            </v-list-tile>
            <v-list-tile @click="">
                <v-list-tile-action>
                    <v-icon>how_to_reg</v-icon>
                </v-list-tile-action>
                <v-list-tile-content>
                    <v-list-tile-title>Sign Up</v-list-tile-title>
                </v-list-tile-content>
            </v-list-tile>
        </v-list>
    </v-navigation-drawer>
    <v-toolbar app fixed clipped-left>
        <v-toolbar-side-icon @click.stop="drawer = !drawer"></v-toolbar-side-icon>
        <v-toolbar-title>Crypto Hype Trader</v-toolbar-title>
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
        margin-top: -120px;
    }
</style>
