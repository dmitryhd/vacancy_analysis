$(function() {
    var cnt = 0;
    var dates = [];
    d_categories = [''];
    d_values = [0];
    function print_plot_info(cnt, dates) {
        $('#cnt').text('Plot: ' + (cnt + 1) + '/' + dates.length);
        $('#date').text('id: ' + dates[cnt]);
        dateObj = new Date(dates[cnt] * 1000);
        $('#date_s').text(dateObj.toString());
    }


    function plot_statistics(tag_name) {
        $.getJSON('/_get_tag_statistics', {
            tag: tag_name
        }, function(data) {
            $('#vac_salary_hist_container').highcharts({
            xAxis: {
                type: 'datetime',
                minPadding: 0.05,
                maxPadding: 0.05
            },
            series: [{
                data: data.max_salary_history
            }]
            })
        })
    }

    $.getJSON('/_get_dates', {}, function(data) {
        dates = data.dates;
        plot_statistics('python');
        print_plot_info(cnt, dates);
    });


});
