// Utility functions common across pages


function round(value, decimals) {
  return Number(Math.round(value + 'e' + decimals) + 'e-' + decimals);
}

Vue.filter('dateTime', function (dt) {
    if (!dt) return ''

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

Vue.filter('capitalize', function (value) {
    if (value === undefined) return '';
    value = value.toString();
    return value.charAt(0).toUpperCase() + value.slice(1)
});

Vue.filter('percent', function (value) {
    if (value === undefined) return '';
    value = value.toString();
    return numeral(value).format('0.00%')
});

Vue.filter('currency', function (value) {
    if (value === undefined) return '';
    value = value.toString();
    return numeral(value).format('$0,0.00');
});

Vue.filter('decimal_2', function (value) {
    if (value === undefined) return '';
    return round(value, 2);
});
