// data and labels for the chart
var labels = bearpop.features.map(function (e) {
    var properties = e.properties; // access the properties field
    return properties.POPULATION_NAME;
});
var popdensity = bearpop.features.map(function (e) {
    var properties = e.properties; // access the properties field
    return properties.EST_POP_DENSITY_2018;
});
;
const data = {
    labels: labels,
    datasets: [
        {//Imports daily high temp data
            label: 'Population Density (# of bears/1000 km2)',
            backgroundColor: 'rgb(50, 130, 50)',
            borderColor: 'rgb(0, 0, 0)',
            data: popdensity,
            yAxisID: 'yPop',
        }
    ]
};
//config for the chart
const config = {
    type: 'bar',
    data: data,
    options: {
        //Data items show up on mouse hover
        responsive: true,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        stacked: false,
        plugins: {
            title: {
                display: true,
                text: 'Grizzly Bear Population Densities of Regions within BC'
            },
        },
        scales: {
            //configuration for temperature data y-axis
            yPop: {
                type: 'linear',
                display: true,
                position: 'left',
            }
        },
    },
}
// render the chart using the configuation
const myChart = new Chart(document.getElementById('myChart'), config);
