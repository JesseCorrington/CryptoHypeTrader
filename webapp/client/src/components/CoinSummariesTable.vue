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
        :rows-per-page-items="[10,20,50,100]"
        class="elevation-1"
        item-key="_id"
        :custom-filter="filterCoins">

        <template slot="items" slot-scope="props">
            <td alight="left">
                <img align="left" :src="props.item.iconUrl" width="32"/>
                <router-link :to="{ name: 'CoinDetail', params: { id: props.item.coin_id, coin: props.item } }">{{ props.item.name }} </router-link>
                ({{ props.item.symbol }})
            </td>

            <td align="right">{{ props.item.market_cap | currency}}</td>
            <td align="right">{{ props.item.price | currency}}</td>
            <td align="right">{{ props.item.volume | currency}}</td>

            <td :class="props.item.growth.price[di] >= 0? 'green--text' : 'red--text'" align="right">
                {{ showPercent === 0? $options.filters.percent(props.item.growth.price[di]) : $options.filters.decimal_2(props.item.growth.price[di])}}
            </td>
            <td :class="props.item.growth.reddit[di] >= 0? 'green--text' : 'red--text'" align="right">
                {{ showPercent === 0? $options.filters.percent(props.item.growth.reddit[di]) : $options.filters.decimal_2(props.item.growth.reddit[di])}}
            </td>
            <td :class="props.item.growth.twitter[di] >= 0? 'green--text' : 'red--text'" align="right">
                {{ showPercent === 0? $options.filters.percent(props.item.growth.twitter[di]) : $options.filters.decimal_2(props.item.growth.twitter[di])}}
            </td>
            <td :class="props.item.growth.code_points[di] >= 0? 'green--text' : 'red--text'" align="right">
                {{ showPercent === 0? $options.filters.percent(props.item.growth.code_points[di]) : $options.filters.decimal_2(props.item.growth.code_points[di])}}
            </td>
            <td :class="props.item.growth.facebook_points[di] >= 0? 'green--text' : 'red--text'" align="right">
                {{ showPercent === 0? $options.filters.percent(props.item.growth.facebook_points[di]) : $options.filters.decimal_2(props.item.growth.facebook_points[di])}}
            </td>
            <td :class="props.item.growth.twitter_followers[di] >= 0? 'green--text' : 'red--text'" align="right">
                {{ showPercent === 0? $options.filters.percent(props.item.growth.twitter_followers[di]) : $options.filters.decimal_2(props.item.growth.twitter_followers[di])}}
            </td>
        </template>
    </v-data-table>
</div>
</template>


<script>
export default {
    props: ['items', 'value'],

    data () {
        return {

            // TODO: consider making headers and di computed properties, and then it will all work like magic
            headers: [
                {text: 'Name', value: 'name', align: "left"},
                {text: 'Market Cap', value: 'market_cap', align: "right"},
                {text: 'Price', value: 'price', align: "right"},
                {text: 'Volume', value: 'volume', align: "right"},
                {text: '24hr price', value: 'growth.price.d1_pct', align: "right"},
                {text: '24hr reddit', value: 'growth.reddit.d1_pct', align: "right"},
                {text: '24hr twitter', value: 'growth.twitter.d1_pct', align: "right"},
                {text: '24hr code', value: 'growth.code_points.d1_pct', align: "right"},
                {text: '24hr FB followers', value: 'growth.facebook_points.d1_pct', align: "right"},
                {text: '24hr twitter subs', value: 'growth.twitter_followers.d1_pct', align: "right"}
            ],
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

                // TODO: implement recent coin add filtering
                if (item.name.toLowerCase().indexOf(searchStr) === -1) return;

                filtered.push(item);
            });

            return filtered;
        }
    },

    computed: {
        growthStyle() {
            return this.showPercent === 0? "_pct" : ""
        }
    },

    watch: {
        showPercent(val) {
            console.log(val);
            console.log(this.showPercent);
        },

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
