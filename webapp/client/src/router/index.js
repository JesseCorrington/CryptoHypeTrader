import Vue from 'vue'
import Router from 'vue-router'
import CoinDetail from '@/components/CoinDetail'
import CoinSummaries from '@/components/CoinSummaries'
import Admin from '@/components/Admin'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'CoinSummaries',
      component: CoinSummaries
    },
    {
      path: '/coin/:id',
      name: 'CoinDetail',
      component: CoinDetail,
      props: true
    },
    {
      path: '/admin',
      name: 'Admin',
      component: Admin
    }
  ]
})
