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
            title: {
                text: 'Динамика средних зарплат'
            },
            series: [{
                name: 'От',
                data: data.max_salary_history
                },
                {
                name: 'До',
                data: data.min_salary_history
                }]
            })
        })
    }

    function plot_salary_histogram(tag_name, date) {
        $.getJSON('/_get_tag_histogram', {
            tag: tag_name,
            date: date
        }, function(data) {
            $('#vac_salary_histogram').highcharts({
                chart: {
                    renderTo: 'container',
                    type: 'column'
                },
                xAxis: {
                    categories: data.bins
                },
                title: {
                    text: 'Гистограмма максимальных зарплат в этот день'
                },
                plotOptions: {
                    column: {
                        groupPadding: 0,
                        pointPadding: 0,
                        borderWidth: 0
                    }
                },

                series: [{
                    name: 'До',
                    data: data.counts
                }]

            })
        })
    }

    $.getJSON('/_get_dates', {}, function(data) {
        dates = data.dates;
        plot_statistics('python');
        plot_salary_histogram('python', dates[cnt]);
        print_plot_info(cnt, dates);
    });


});
