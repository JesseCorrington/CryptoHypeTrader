// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'
import App from './App'
import router from './router'
import numeral from 'numeral'
import HighchartsVue from 'highcharts-vue'
import Highcharts from 'highcharts'
import stockInit from 'highcharts/modules/stock'
import CoinChart from '@/components/CoinChart'
import CoinSummariesTable from '@/components/CoinSummariesTable'
import CoinSummaries from '@/components/CoinSummaries'
import Admin from '@/components/Admin'
import CurrencyField from '@/components/CurrencyField'
import TaskTable from '@/components/TaskTable'
import CommentsTable from '@/components/CommentsTable'

Vue.config.productionTip = false;

Vue.use(Vuetify);

stockInit(Highcharts);
Vue.use(HighchartsVue);

Vue.component('coin-chart', CoinChart);
Vue.component('coin-summaries-table', CoinSummariesTable);
Vue.component('coin-summaries', CoinSummaries);
Vue.component('admin', Admin);
Vue.component('currency-field', CurrencyField);
Vue.component('task-table', TaskTable);
Vue.component('comments-table', CommentsTable)

/* eslint-disable no-new */
new Vue({
    el: '#app',
    router,
    components: { App },
    template: '<App/>'
});


function round(value, decimals) {
    return Number(Math.round(value + 'e' + decimals) + 'e-' + decimals);
}

Vue.filter('dateTime', function (dt) {
    if (!dt) return '';

    if (typeof(dt) !== Date) {
        dt = new Date(dt);
    }

    var m = dt.getMonth() + 1;
    var d = dt.getDate();
    var y = dt.getFullYear();
    var hr = dt.getHours();
    var mn = dt.getMinutes();
    var sc = dt.getSeconds();

    return `${m}/${d}/${y} ${hr}:${mn}:${sc}`;
});

Vue.filter('timeInterval', function(ms) {
    const SECOND = 1000;
    const MINUTE = SECOND * 60;
    const HOUR = MINUTE * 60;
    var remainder = ms;

    var h = Math.floor(remainder / HOUR);
    remainder -= h * HOUR;

    var m = Math.floor(remainder / MINUTE);
    remainder -= m * MINUTE;

    var s = Math.floor(remainder / SECOND);
    remainder -= s * SECOND;

    return `${h}:${m}:${s}:${remainder}`;
});

Vue.filter('capitalize', function (value) {
    if (value === undefined || value === null) return '';
    value = value.toString();
    return value.charAt(0).toUpperCase() + value.slice(1)
});

Vue.filter('percent', function (value) {
    if (value === undefined || value === null) return '';
    value = value.toString();
    return numeral(value).format('0.00%')
});

Vue.filter('currency', function (value) {
    if (value === undefined || value === null) return '';
    value = value.toString();
    return numeral(value).format('$0,0.00');
});

Vue.filter('number', function (value) {
    if (value === undefined || value === null) return '';
    value = value.toString();
    return numeral(value).format('0,0');
});

Vue.filter('decimal_2', function (value) {
    if (value === undefined || value === null) return '';
    return round(value, 2);
});
