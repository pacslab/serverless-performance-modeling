var api_address_base = "http://savi.nima-dev.com:5000/"

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

function getProps() {
    console.log("submitting...");
    var data = getFormJsonData('#form-workload-props');
    console.log(data);
    console.log(JSON.stringify(data));

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
            var value = props[key];
            resultHtml += "<tr>";
            resultHtml += "<th scope=\"row\">" + idx + "</th>";
            resultHtml += "<td>" + key + "</td>";
            resultHtml += "<td>" + value + "</td>";
            resultHtml += "</tr>";
            // do something with "key" and "value" variables
        }

        console.log(resultHtml);


        $("#props-body").html(resultHtml);
    });
}

$("#form-workload-props").submit(function (event) {
    event.preventDefault();

    getProps();
});

// Run on page load
getProps();
