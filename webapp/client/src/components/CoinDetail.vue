<template>
<div>
    <v-card>
        <h1>Coin Detail</h1>
        <img :src="coin.iconUrl" width="64"/>
        <table>
            <tr>
                <td>Symbol</td><td>{{coin.symbol}}</td>
            </tr>
            <tr>
                <td>Name</td><td>{{coin.name}}</td>
            </tr>
            <tr>
                <td>Subreddit</td><td><a :href="coin.subredditUrl">{{coin.subreddit}}</a></td>
            </tr>
            <tr>
                <td>Twitter</td><td><td><a :href="coin.twitterUrl">{{coin.twitter}}</a></td>
            </tr>
        </table>
    </v-card>

    <v-card>
        Recent Comments

        <v-data-table
            :headers="headers"
            :items="coin.comments"
            :rows-per-page-items="[10]"
            class="elevation-1">

            <template slot="items" slot-scope="props">
                <td>{{props.item.date | dateTime}}</td>
                <td align="left">{{props.item.text}}</td>
                <td>{{props.item.score}}</td>
                <td>{{props.item.sentiment | decimal_2}}</td>
                <td>
                    <img v-if="props.item.platform === 'reddit_comments'" src="/static/images/reddit_icon.png" width="32"/>
                    <img v-else src="/static/images/twitter_icon.png" width="32"/>
                </td>
            </template>
        </v-data-table>
    </v-card>
</div>
</template>


<script>
import Services from '@/services/Services'

export default {
    name: 'CoinDetail',
    props: ['coin'],

    data () {
        return {
            headers: [
                {text: 'Date', value: 'date', align: 'left'},
                {text: 'text', value: 'text', align: 'left'},
                {text: 'Score', value: 'score', align: 'left'},
                {text: 'Sentiment', value: 'sentiment', align: 'left'},
                {text: 'Platform', value: 'platform', align: 'left'},
            ]
        }
    },

    mounted () {
        this.coin.loadComments();
    }
}
</script>
