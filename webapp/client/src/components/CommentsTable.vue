<template>
<v-data-table
    :headers="headers"
    :items="comments"
    :rows-per-page-items="[20,50]"
    :pagination.sync="pagination"
    class="elevation-1"
    item-key="_id">

    <template slot="headerCell" slot-scope="props">
        <strong>{{ props.header.text }}</strong>
    </template>

    <template slot="items" slot-scope="props">
        <td align="left">{{props.item.date | dateTime}}</td>
        <td align="left">{{props.item.platform}}</td>
        <td align="left">{{props.item.text}}</td>
        <td align="left">{{props.item.score}}</td>
        <td align="left">{{props.item.sentiment | decimal_2}}</td>
        <td align="left">{{props.item.coin_id}}</td>
    </template>
    </v-data-table>
</template>

<script>
    import Services from '@/services/Services'

    export default {
        name: "TaskTable",

        data () {
            return {
                headers: [
                    {text: 'Date', value: 'date', align: 'left'},
                    {text: 'Platform', value: 'platform', align: 'left'},
                    {text: 'Text', value: 'text', align: 'left'},
                    {text: 'Score', value: 'score', align: 'left'},
                    {text: 'Sentiment', value: 'sentiment', align: 'left'},
                    {text: 'Symbol', value: 'coin_id', align: 'left'},
                ],
                pagination: {
                    sortBy: 'date',
                    descending: true
                },
                comments: []
            }
        },

        mounted() {
            this.loadData();
        },

        methods: {
            async loadData() {
                const response = await Services.getRecentComments();
                this.comments = response.data;
            },
        }
    }
</script>
