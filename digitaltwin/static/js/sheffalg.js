var count = 1;

var layout = {
    grid: { rows: 2, columns: 3, pattern: 'independent', row_heights: [200, 200, 200] },
    autosize: false,
    showlegend: false,
    width: 1500,
    height: 1100,
    margin: {
        l: 50,
        r: 50,
        b: 100,
        t: 100,
        pad: 4
    },
    annotations: [{
        text: "1st storey acceleration",
        font: {
            size: 24,
            color: 'blue',
        },
        showarrow: false,
        align: 'left',
        x: 0.03, //position in x domain
        y: 1.07, //position in y domain
        xref: 'paper',
        yref: 'paper',
    },
    {
        text: "2nd storey acceleration",
        font: {
            size: 24,
            color: 'orange',
        },
        showarrow: false,
        align: 'center',
        x: 0.5, //position in x domain
        y: 1.07,  // position in y domain
        xref: 'paper',
        yref: 'paper',
    },
    {
        text: "3rd storey acceleration",
        font: {
            size: 24,
            color: 'green',
        },
        showarrow: false,
        align: 'right',
        x: 0.95, //position in x domain
        y: 1.07,  // position in y domain
        xref: 'paper',
        yref: 'paper',
    }
    ],
    //title: {
    //   text: '3rd Storey Acceleration',
    //   font: {
    //        family: 'Times-Roman, monospace',
    //        size: 24
    //    },
    //   xref: 'paper',
    //   x: 0.05,
    //},
    xaxis: {
        //showgrid: true,
        //zeroline: true,
        title: '$\t{Time  }(s)$',
        font: {
            family: 'Times-Roman, monospace',
            size: 24
        },
        anchor: 'y1'

    },
    yaxis: {
        //autorange: true,
        title: '$\t{Acceleration } (m/s^2)$',
        font: {
            family: 'Times-Roman, monospace',
            size: 24
        },
        anchor: 'x1'
    },
    xaxis2: {
        //showgrid: true,
        //zeroline: true,
        title: '$\t{Time  }(s)$',
        font: {
            family: 'Times-Roman, monospace',
            size: 24
        },
        anchor: 'y2'

    },
    yaxis2: {
        //autorange: true,
        title: '$\t{Acceleration } (m/s^2)$',
        font: {
            family: 'Times-Roman, monospace',
            size: 24
        },
        anchor: 'x2'
    },
    xaxis3: {
        //showgrid: true,
        //zeroline: true,
        title: '$\t{Time  }(s)$',
        font: {
            family: 'Times-Roman, monospace',
            size: 24
        },
        anchor: 'y3'

    },
    yaxis3: {
        //autorange: true,
        title: '$\t{Acceleration } (m/s^2)$',
        font: {
            family: 'Times-Roman, monospace',
            size: 24
        },
        anchor: 'x3'
    },
    xaxis4: {
        //showgrid: true,
        //zeroline: true,
        title: '1st storey acceleration',
        font: {
            family: 'Times-Roman, monospace',
            size: 24
        },
        anchor: 'y4'

    },
    yaxis4: {
        //autorange: true,
        title: 'Amplitude (m)',
        font: {
            family: 'Times-Roman, monospace',
            size: 24
        },
        anchor: 'x4'
    },
    xaxis5: {
        //showgrid: true,
        //zeroline: true,
        title: '2nd storey acceleration',
        font: {
            family: 'Times-Roman, monospace',
            size: 24
        },
        anchor: 'y5'

    },
    yaxis5: {
        //autorange: true,
        title: 'Amplitude (m)',
        font: {
            family: 'Times-Roman, monospace',
            size: 24
        },
        anchor: 'x5'
    },
    xaxis6: {
        //showgrid: true,
        //zeroline: true,
        title: '3rd storey acceleration',
        font: {
            family: 'Times-Roman, monospace',
            size: 24
        },
        anchor: 'y6'

    },
    yaxis6: {
        //autorange: true,
        title: 'Amplitude (m)',
        font: {
            family: 'Times-Roman, monospace',
            size: 24
        },
        anchor: 'x6'
    },
    hovermode: !1
};

$(document).ready(function () {
    setInterval(ajaxd, 500);
});

function ajaxd() {
    $.ajax({
        url: "/udsheff",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: { value: count },
        dataType: "json",
        success: function (data) {
            Plotly.react('sheffgraph', data, layout = layout);
            console.log(count);
            if (count > 178) {
                count = 0;
            } else {
                count++;
            }
        }
    });
}