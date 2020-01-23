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
    console.log($('#form-workload-props').serialize());
    var data = getFormJsonData('#form-workload-props');
    console.log(data);
    console.log(JSON.stringify(data));
});
