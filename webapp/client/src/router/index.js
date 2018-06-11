import Vue from 'vue'
import Router from 'vue-router'
import CoinDetail from '@/components/CoinDetail'
import CoinSummaries from '@/components/CoinSummaries'
import Admin from '@/components/Admin'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/coin/:id',
      name: 'CoinDetail',
      component: CoinDetail
    },
    {
      path: '/coinsummaries',
      name: 'CoinSummaries',
      component: CoinSummaries
    },
    {
      path: '/admin',
      name: 'Admin',
      component: Admin
    }
  ]
})
