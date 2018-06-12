<template>
  <div class="posts">
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
  </div>
</template>

<script>
import Services from '@/services/Services'
export default {
  name: 'CoinDetail',

  props: ['coin'],

  mounted () {
      console.log(this.coin);
  }
}
</script>
</style>
