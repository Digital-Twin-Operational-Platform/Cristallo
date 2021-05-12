var count = 1;

var layout = {
    grid: { rows: 3, columns: 1, pattern: 'independent', row_heights: [200, 200, 200] },
    paper_bgcolor: 'rgba(255,0,0,0)',
    plot_bgcolor: 'rgba(255,255,0,0)',
    autosize: false,
    width: 1000,
    height: 1200,
    margin: {
        l: 50,
        r: 50,
        b: 100,
        t: 100,
        pad: 4
    },
    xaxis: {
        //showgrid: true,
        //zeroline: true,
        title: '$\t{Time  }(s)$',
        font: {
            family: 'Arial, monospace',
            size: 30
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
    hovermode: !1
};

$(document).ready(function () {
    setInterval(ajaxd, 100);
});

function ajaxd() {
    $.ajax({
        url: "/update",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: { value: count },
        dataType: "json",
        success: function (data) {
            Plotly.react('bargraph', data, layout = layout);
            console.log(count);
            if (count > 178) {
                count = 0;
            } else {
                count++;
            }
        }
    });
}