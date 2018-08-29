<template>
<div>
    <v-toolbar>
        <v-text-field append-icon="search" label="Search" single-line hide-details v-model="search"></v-text-field>
        <v-spacer></v-spacer>

        <v-btn-toggle v-model="selectedCurrency" mandatory>
            <v-toolbar-items>
                <v-btn>USD</v-btn>
                <v-btn>BTC</v-btn>
            </v-toolbar-items>
        </v-btn-toggle>

        <v-spacer></v-spacer>
        <v-btn-toggle v-model="showPercent">
            <v-toolbar-items>
                <v-btn>%</v-btn>
            </v-toolbar-items>
        </v-btn-toggle>

        <v-btn-toggle v-model="selectedTimeInterval" mandatory>
            <v-toolbar-items v-for="interval in timeIntervals" :key="interval.key">
                <v-btn :key="interval.key">{{interval.disp}}</v-btn>
            </v-toolbar-items>
        </v-btn-toggle>

        <v-btn flat icon @click.stop="settingsDialog = true">
            <v-icon>settings</v-icon>
        </v-btn>
    </v-toolbar>

    <v-dialog v-model="settingsDialog" max-width="500px">
        <v-card>
            <v-card-title>
                Filter Settings
            </v-card-title>
            <v-card-text>
                <v-container grid-list-md text-xs-center>
                    <v-layout row wrap>
                        <v-flex xs12>
                            <v-checkbox v-model="filters.reddit" label="Has Subreddit" value="subreddit"></v-checkbox>
                        </v-flex>
                        <v-flex xs12>
                            <v-checkbox v-model="filters.twitter" label="Has Twitter" value="twitter"></v-checkbox>
                        </v-flex>
                        <v-flex xs12>
                            <v-checkbox v-model="filters.recent" label="Recently Added" value="newCoin"></v-checkbox>
                        </v-flex>

                        <v-flex xs4>
                            Price Range
                            <currency-field v-model="filters.price.min" label="min" prefix="$"></currency-field>
                            <currency-field v-model="filters.price.max" label="max" prefix="$"></currency-field>
                        </v-flex>

                        <v-flex xs4>
                            Market Cap Range
                            <currency-field v-model="filters.market_cap.min" label="min" prefix="$"></currency-field>
                            <currency-field v-model="filters.market_cap.max" label="max"prefix="$"></currency-field>
                        </v-flex>

                        <v-flex xs4>
                            Volume Range
                            <currency-field v-model="filters.volume.min" label="min" prefix="$"></currency-field>
                            <currency-field v-model="filters.volume.max" label="max" prefix="$"></currency-field>
                        </v-flex>
                    </v-layout>
                </v-container>
            </v-card-text>
            <v-card-actions>
                <v-btn flat icon @click.stop="settingsDialog=false">
                    <v-icon>close</v-icon>
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <v-data-table
        :headers="headers"
        :search="search"
        :pagination.sync="pagination"
        :items="items"
        :rows-per-page-items="[20,50,100]"
        class="elevation-1"
        item-key="_id"
        :custom-filter="filterCoins">

        <template slot="headerCell" slot-scope="props">
            <strong>{{ props.header.text }}</strong>
        </template>

        <template slot="items" slot-scope="props">
            <td :background="props.item.iconUrl" class="coincell">
                <div class="coincell">{{ props.item.name }}</div>
            </td>

            <td align="right">{{ formatCurrency(props.item.market_cap)}}</td>
            <td align="right">{{ formatCurrency(props.item.price)}}</td>
            <td align="right">{{ formatCurrency(props.item.volume)}}</td>

            <td v-for="col in growthCols" :class="props.item.growth[col][di] >= 0? 'green--text' : 'red--text'" align="right">
                {{formatGrowth(props.item.growth[col][di])}}
            </td>
        </template>
    </v-data-table>
</div>
</template>


<script>
import numeral from 'numeral'

export default {
    props: ['items', 'value'],

    data () {
        return {
            headers: [
                {text: 'Name', value: 'name', align: "left"},
                {text: 'Market Cap', value: 'market_cap', align: "right"},
                {text: 'Price', value: 'price', align: "right"},
                {text: 'Volume', value: 'volume', align: "right"},
                {text: '1d Price', value: 'growth.price.d1_pct', align: "right"},
                {text: '1d Reddit', value: 'growth.reddit.d1_pct', align: "right"},
                {text: '1d Twitter', value: 'growth.twitter.d1_pct', align: "right"},
                {text: '1d GitHub', value: 'growth.code_points.d1_pct', align: "right"},
                {text: '1d Facebook', value: 'growth.facebook_points.d1_pct', align: "right"},

            ],
            growthCols: ["price", "reddit", "twitter", "code_points", "facebook_points"],

            search: "",
            pagination: {
                sortBy: 'market_cap',
                descending: true
            },
            timeIntervals: [
                {disp: '12h', key: "h12"},
                {disp: '1d', key: "d1"},
                {disp: '3d', key: "d3"},
                {disp: '5d', key: "d5"},
                {disp: '7d', key: "d7"},
            ],
            selectedTimeInterval: 1,
            di: "d1_pct",
            selectedCurrency: "USD",
            showPercent: 0,
            settingsDialog: false,
            selectedFilters: [],

            filters: {
                price: {},
                market_cap: {},
                volume: {},
                subreddit: false,
                twitter: false,
                recent: false
            }
        }
    },

    methods: {
        updateGrowthCols() {
            var key = this.di;;
            var disp = this.timeIntervals[this.selectedTimeInterval].disp;

            this.headers[4].text = `${disp} Price`;
            this.headers[4].value = `growth.price.${key}`;

            this.headers[5].text = `${disp} Reddit`;
            this.headers[5].value = `growth.reddit.${key}`;

            this.headers[6].text = `${disp} Twitter`;
            this.headers[6].value = `growth.twitter.${key}`;

            this.headers[7].text = `${disp} Code Points`;
            this.headers[7].value = `growth.code_points.${key}`;

            this.headers[8].text = `${disp} FB Followers`;
            this.headers[8].value = `growth.facebook_points.${key}`;
        },

        filterCoins(items, searchStr, filter) {
            var filtered = []
            var rangeFilters = ["price", "market_cap", "volume"];
            searchStr = searchStr.toLowerCase();

            items.forEach((item) => {
                for (var i = 0; i < rangeFilters.length; i++) {
                    var key = rangeFilters[i];
                    if (this.filters[key].min && item[key] < this.filters[key].min) return;
                    if (this.filters[key].max && item[key] > this.filters[key].max) return;
                }

                if (this.filters.subreddit && !item.subreddit) return;
                if (this.filters.twitter && !item.twitter) return;

                if (item.name.toLowerCase().indexOf(searchStr) === -1 &&
                    item.symbol.toLowerCase().indexOf(searchStr) === -1) return;

                if (this.filters.recent && !item.recentlyAdded) return;

                filtered.push(item);
            });

            return filtered;
        },

        formatCurrency(usdValue) {
            if (this.selectedCurrency === 0) {
                if (usdValue === undefined || usdValue === null) return "";
                return numeral(usdValue).format('$0,0.00');
            }
            else {
                var btc = usdValue / this.items[0].price;
                return "₿ " + btc.toFixed(6);
            }
        },

        formatGrowth(val) {
            if (val === undefined) {
                val = 0;
            }

            if (this.showPercent === 0) {
                return numeral(val).format('0.00%')
            }

            return val.toFixed(2);
        }
    },

    computed: {
        growthStyle() {
            return this.showPercent === 0? "_pct" : ""
        }
    },

    watch: {
        selectedTimeInterval(val) {
            this.di = this.timeIntervals[this.selectedTimeInterval].key + this.growthStyle;
        },

        growthStyle() {
            this.di = this.timeIntervals[this.selectedTimeInterval].key + this.growthStyle;
        },

        di() {
            this.updateGrowthCols();
        },
    }
};
</script>

<style>

.coincell {
    background-size: 32px;
    background-position: 10px center;
    margin-left: 20%;
    vertical-align: middle;
    text-align: left;
    font-weight: bold;
}
</style>
