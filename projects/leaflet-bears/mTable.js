//when page loads create table header
window.onload = function () {
    document.getElementById("jsontable").innerHTML = " <tr><th> Population Name </th><th> Population Density (# of bears/1000 km2) </th></tr>";
    //navigate through the json array to get the data Month and AveTmpH
    // for each line in the array write out the data in a table rows
    bearpop.features.forEach(function (e) {
        var properties = e.properties; // access the properties field
        document.getElementById("jsontable").innerHTML += " <tr><td> " + properties.POPULATION_NAME + " </td><td> " + properties.EST_POP_DENSITY_2018 + " </td></tr>";
    });
};