// var api_address_base = "https://api.nima-dev.com/serverless-performance-modeling/"
var api_address_base = "http://127.0.0.1:5000/"

function updateArrivalRateVal(val) {
    document.getElementById('arrivalRateVal').innerHTML = val;
}

// Update Arrival Rate Value
document.getElementById('arrivalRateVal').innerHTML = document.getElementById('arrivalRate').value

function getFormJsonData(formid) {
    var data = $(formid).serializeArray().reduce(function (obj, item) {
        obj[item.name] = item.value;
        return obj;
    }, {});
    return data;
}


// for plots
var plotly_config = { responsive: true }
var plot1_trace = [
    {
        type: "scatter",
        name: 'Probability of Cold Start',
        x: [],
        y: [],
    },
    {
        type: "scatter",
        name: 'Instance Utilization',
        yaxis: 'y2',
        x: [],
        y: [],
    },
]
var plot2_trace = [
    {
        type: "scatter",
        name: 'Total',
        x: [],
        y: [],
    },
    {
        type: "scatter",
        name: 'Running',
        x: [],
        y: [],
    },
    {
        type: "scatter",
        name: 'Idle',
        x: [],
        y: [],
    }
]
function preparePlots() {
    let layout1 = {
        // title: 'Instance Utilization and Probability of Cold Start',
        xaxis: {
            type: 'log',
            autorange: true,
            title: "Arrival Rate (reqs/sec)"
        },
        yaxis: {
            title: "Cold Start Probability (%)"
        },
        yaxis2: {
            title: 'Instance Utilization (%)',
            overlaying: 'y',
            side: 'right'
        }
    }
    Plotly.newPlot('plot1', plot1_trace, layout1, plotly_config)

    let layout2 = {
        // title: 'Instance Count',
        xaxis: {
            type: 'log',
            autorange: true,
            title: "Arrival Rate (reqs/sec)"
        },
        yaxis: {
            // type: 'log',
            autorange: true,
            title: "Number of Instances"
        },
    }
    Plotly.newPlot('plot2', plot2_trace, layout2, plotly_config)
}

function updatePlots(plot_vals) {
    // redraw plot1
    plot1_trace[0].x = plot_vals['arrival_rate']
    plot1_trace[0].y = plot_vals['cold_prob'].map((val) => 100 * val)
    plot1_trace[1].x = plot_vals['arrival_rate']
    plot1_trace[1].y = plot_vals['avg_utilization'].map((val) => 100 * val)
    Plotly.redraw('plot1')

    // redraw plot2
    plot2_trace[0].x = plot_vals['arrival_rate']
    plot2_trace[0].y = plot_vals['avg_server_count']
    plot2_trace[1].x = plot_vals['arrival_rate']
    plot2_trace[1].y = plot_vals['avg_running_count']
    plot2_trace[2].x = plot_vals['arrival_rate']
    plot2_trace[2].y = plot_vals['avg_idle_count']
    Plotly.redraw('plot2')
}

function getProps() {
    var data = getFormJsonData('#form-workload-props');
    console.log(data);
    console.log(JSON.stringify(data));

    // get props
    let url = api_address_base + "perfmodel/api/props";
    $.ajax({
        method: "POST",
        url: url,
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify(data)
    }).done(function (props) {
        console.log(props);

        let resultHtml = ""
        let idx = 0;
        for (var key in props) {
            idx++;

            if (key == "plot_vals") continue

            var value = props[key];
            resultHtml += "<tr>";
            resultHtml += "<th scope=\"row\">" + idx + "</th>";
            resultHtml += "<td>" + key + "</td>";
            resultHtml += "<td>" + value + "</td>";
            resultHtml += "</tr>";
        }

        $("#props-body").html(resultHtml);

        // update plots
        updatePlots(props['plot_vals'])
    });
}

$("#form-workload-props").submit(function (event) {
    event.preventDefault();

    getProps();
});

// Run on page load
preparePlots();
getProps();
