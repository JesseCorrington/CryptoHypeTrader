<template>
  <div class="posts">
    <h1>Coin Detail</h1>
      <table>
        <tr>
          <td>Symbol</td><td>{{ symbol }}</td>
        </tr>
        <tr>
          <td>Name</td><td>{{ name }}</td>
        </tr>
        <tr>
          <td>Subreddit</td><td>{{ subreddit }}</td>
        </tr>
          <tr>
          <td>Twitter</td><td>{{ twitter }}</td>
        </tr>
      </table>
  </div>
</template>

<script>
import Services from '@/services/Services'
export default {
  name: 'CoinDetail',
  data () {
    return {
      symbol: '',
      name: '',
      subreddit: '',
      twitter: ''
    }
  },
  mounted () {
    this.getCoin()
  },
  methods: {
    async getCoin () {

      // TODO: allow this to work also if route passes the pre laoded coin in (should work both)
      const response = await Services.getCoin({
        id: this.$route.params.id
      })
      this.symbol = response.data.symbol;
      this.name = response.data.name;
      this.subreddit = response.data.subreddit;
      this.twitter = response.data.twitter;
    }
  }
}
</script>
</style>
