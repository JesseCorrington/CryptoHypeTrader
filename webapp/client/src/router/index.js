import Vue from 'vue'
import Router from 'vue-router'
import CoinDetail from '@/components/CoinDetail'
import CoinSummaries from '@/components/CoinSummaries'
import Admin from '@/components/Admin'
import Main from '@/components/Main'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'Main',
      component: Main
    },
    {
      path: '/coin/:id',
      name: 'CoinDetail',
      component: CoinDetail,
      props: true
    }
  ]
})
