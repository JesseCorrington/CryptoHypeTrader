function sortBy(arr, sortkey) {
    var reverse = 1;
    if (sortkey.charAt(0) === "-") {
        reverse = -1;
        sortkey = sortkey.substr(1);
    }

    arr.sort((a, b) => {
        a = a[sortkey];
        b = b[sortkey];

        c = -1;
        c = -1 * reverse;

        if (a < b) return -1 * reverse;
        if (a > b) return 1 * reverse;
        return 0;
    });
}

function filterArrayObjects(arr, filter) {
    var filtered = [];
    arr.forEach((obj) => {
        for (var filterkey in filter) {
            var ops = filter[filterkey];

            // TODO: this feels wrong, since gt is >=, not >
            // maybe we should have gt, gte, lt, and lte
            if (ops.lt && ops.lt !== NaN && obj[filterkey] >= ops.lt) {
                return;
            }
            if (ops.gt && ops.gt !== NaN && obj[filterkey] <= ops.gt) {
                return;
            }
            if (ops.exclude && ops.exclude.includes(obj.symbol)) {
                return;
            }
        }

        filtered.push(obj);
    });

    return filtered;
}

function getInputFloat(id) {
    var text = $("#" + id).val();
    return (text && text.length > 0)? parseFloat(text) : undefined
}

function getInputInt(id) {
    var text = $("#" + id).val()
    return (text && text.length > 0)? parseInt(text) : undefined
}

function getInputArray(id) {
    var text = $("#" + id).val();
    var arr = text.split(",");
    for (var i = 0; i < arr.length; i++) {
        arr[i] = arr[i].trim();
    }
    return arr;
}

function arrayToObject(arr, keyname) {
    var ret = {};
    for (var i = 0; i < arr.length; i++) {
        var key = arr[i][keyname];
        ret[key] = arr[i];
    }
    return ret;
}

function deleteRequest(path, id, callback) {
    $.ajax({
        url: path + '/' + id,
        type: 'DELETE',
        success: callback
    });
}

function createRequest(path, obj, callback) {
    $.ajax({
        url: path,
        type: 'POST',
        data: JSON.stringify(obj),
        contentType: 'application/json',
        success: callback
    });
}

function formatDateTime(dt) {
    if (typeof(dt) !== Date) {
        dt = new Date(dt);
    }

    var m = dt.getMonth();
    var d = dt.getDate();
    var y = dt.getFullYear();

    var hr = dt.getHours();
    var mn = dt.getMinutes();
    var sc = dt.getSeconds();

    return `${m}/${d}/${y} ${hr}:${mn}:${sc}`;
}

function formatElapsedTime(milliseconds) {
    // TODO: be better to do something like, x year, x days, x mins
    var days = milliseconds / 1000 / 60 / 60 / 24;
    return days.toFixed(2) + " days";
}



// TODO: need an entry point where we install filters
Vue.filter('formatDateTime', function (dt) {
    if (!dt) return ''

    if (typeof(dt) !== Date) {
        dt = new Date(dt);
    }

    var m = dt.getMonth();
    var d = dt.getDate();
    var y = dt.getFullYear();
    var hr = dt.getHours();
    var mn = dt.getMinutes();
    var sc = dt.getSeconds();

    return `${m}/${d}/${y} ${hr}:${mn}:${sc}`;
})

Vue.filter('capitalize', function (value) {
    if (value === undefined) return ''
    value = value.toString()
    return value.charAt(0).toUpperCase() + value.slice(1)
});