const logSlider = (position) => {
    const minp = 0;
    const maxp = 100;
    const minv = Math.log(1);
    const maxv = Math.log(1000000000);
    const scale = (maxv - minv) / (maxp - minp);
    return Math.exp(minv + scale * (position - minp));
};

const logPosition = (value) => {
    const minp = 0;
    const maxp = 100;
    const minv = Math.log(1);
    const maxv = Math.log(1000000000);
    const scale = (maxv - minv) / (maxp - minp);
    return (Math.log(value) - minv) / scale + minp;
};

const formatValue = (value) => {
    if (value >= 1000000000) return '1B €';
    if (value >= 1000000) return (value / 1000000).toFixed(1) + 'M €';
    if (value >= 1000) return (value / 1000).toFixed(1) + 'K €';
    return value.toLocaleString() + ' €';
};

$(document).ready(function () {
    $("#slider-range").slider({
        range: true,
        min: 0,
        max: 100,
        values: [
            logPosition(Math.max(1, initialMinValue)),
            logPosition(initialMaxValue)
        ],
        slide: function (event, ui) {
            const realValues = [
                Math.floor(logSlider(ui.values[0])),
                Math.floor(logSlider(ui.values[1]))
            ];

            $("#minValue").text(formatValue(realValues[0]));
            $("#maxValue").text(formatValue(realValues[1]));
            $("#min_value_input").val(realValues[0]);
            $("#max_value_input").val(realValues[1]);
        }
    });
});
