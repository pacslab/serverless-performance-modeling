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

$("#form-workload-props").submit(function (event) {
    event.preventDefault();

    console.log("submitting...");
    var data = getFormJsonData('#form-workload-props');
    console.log(data);
    console.log(JSON.stringify(data));

    let url = api_address_base + "perfmodel/api/props";
    $.ajax({
        method: "POST",
        url: url,
        dataType: "json",
        contentType:"application/json",
        data: JSON.stringify(data)
    }).done(function (data) {
        console.log(data)
    });
});
