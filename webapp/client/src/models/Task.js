export default class Task {
    constructor(data) {
        for (var key in data) {
            this[key] = data[key];

            if (this[key] === null)
                this[key] = 0;
        }

        // Add computed properties to help build the UI
        var endTime = this.running ? new Date().getTime() : this.end_time;
        this.elapsed_time = endTime - this.start_time;
        this.percent_done *= 100;

        if (this.failed || this.canceled) {
            this.statusIcon = 'error';
            this.statusIconColor = 'red';
            this.statusIconTooltip = this.failed ? 'failed' : 'canceled';
        } else {
            this.statusIcon = 'done';
            this.statusIconTooltip = 'success';
        }
    }
}


Task.prototype.toString = function() {
    return this.name;
};
