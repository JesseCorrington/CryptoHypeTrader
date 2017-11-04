"use strict"

// TODO: do we even need this anymore?
class Component {
    constructor(container) {
        if (container === undefined) {
            // TODO: get rid of this eventually, so we always use the create,
            // then add to parent model
            this._container = $("<div>");
        }
        else if (typeof(container) === "string") {
            this._container = $("#" + container);
        }
        else {
            this._container = container;
        }
    }
}

class Table extends Component {
    constructor(container, width, height) {
        if (!container) {
            container = $("<table>", {class: 'tableclass'});
        }

        super(container);

        this._data = [];
        this._dataView = [];
        this._cols = [];
    }

    render() {
        var table = this._container;
        table.empty();

        var thead = $("<thead>");
        table.append(thead);

        var self = this;
        for (let c = 0; c < this._cols.length; c++) {
            var header = this._cols[c].header

            var sortDir = this._cols[c].sortDir;
            if (sortDir) {
                header += sortDir === 1? "▲" : "▼";
            }

            var th = $("<th>").html(header);
            th.click(() =>{
                self.sortByColumn(c);
            });

            thead.append(th);
        }

        for (var r = 0; r < this._dataView.length; r++) {
            var row = $("<tr>");
            table.append(row);

            for (var c = 0; c < this._cols.length; c++) {
                var cell = this._dataView[r][this._cols[c].key];

                if(typeof(cell) === "boolean"){
                    cell = cell.toString()
                }

                if (this._dataFormats) {
                    var cellFormat = this._dataFormats[this._cols[c].key]

                    if (cellFormat) {
                        // TODO: distinguish date format in a non hack way
                        if (cellFormat === "DateTime") {
                            cell = formatDate(cell);
                        }
                        else if (cellFormat === "ElapsedTime") {
                            cell = formatElapsedTime(cell);
                        }
                        else {
                            cell = numeral(cell).format(cellFormat)
                        }
                    }
                }

                row.append($("<td>").html(cell));
            }
        }

        //this._container.append(table);
    }

    sortByColumn(col) {
        var sortDir = this._cols[col].sortDir;
        this.resetColumnSort();

        sortDir = sortDir? -sortDir : 1;
        this._cols[col].sortDir = sortDir;

        var sortkey = this._cols[col].key;

        this._dataView.sort((a, b) => {
            if (a[sortkey] < b[sortkey]) return -sortDir;
            if (a[sortkey] > b[sortkey]) return sortDir;
            return 0;
        });

        this.render();
    }

    resetColumnSort() {
        this._cols.forEach((col) => {
            col.sortDir = undefined;
        });
    }

    setColumns(cols) {
        this._cols = cols;
        this.resetColumnSort();
    }

    setData(data, formats) {
        this._data = data;
        this._dataFormats = formats;

        // Shallow copy for the view, so we don't modify the original list
        this._dataView  = data.slice();

        this.render();
    }

    sortRows(sortkey) {
        sortBy(this._dataView, sortkey);
        this.render();
    }

    filterRows(filter) {
        this._dataView = filterArrayObjects(this._data, filter);
        this.render();
    }
}