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
    function get_url_parameter(sParam) {
        var sPageURL = window.location.search.substring(1);
        var sURLVariables = sPageURL.split('&');
        for (var i = 0; i < sURLVariables.length; i++) {
            var sParameterName = sURLVariables[i].split('=');
            if (sParameterName[0] == sParam) {
                return sParameterName[1];
            }
        }
    }

    function find_current_timestamp(dates, timestamp) {
        // return cnt or 0
        for (var i = 0; i < dates.length; i++) {
            if (dates[i] == timestamp) {
                return i;
            }
        }
        return 0;
    }

    function plot_statistics(tag_name) {
        $.getJSON('/_get_tag_statistics', {
            tag: tag_name
        }, function(data) {
            $('#vac_salary_hist_container').highcharts({
            xAxis: { type: 'datetime', minPadding: 0.05, maxPadding: 0.05 },
            title: { text: 'Динамика средних зарплат' },
            yAxis: { title: {text: 'Средняя зарплата (руб)'}},
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
                chart: { type: 'column' },
                xAxis: { categories: data.bins },
                yAxis: { title: {text: 'Количество вакансий'}},
                title: { text: 'Гистограмма максимальных зарплат в этот день' },
                plotOptions: {
                    column: {
                        groupPadding: 0,
                        pointPadding: 0,
                        borderWidth: 0
                    }
                },
                series: [{
                    name: 'Количество вакансий',
                    data: data.counts,
            dataLabels: {
                enabled: true,
            color: '#FFFFFF',
            align: 'right',
            format: '{point.y:f}', // one decimal
            y: 30, // 10 pixels down from the top
            x: -15,
            style: {
                fontSize: '13px',
                fontFamily: 'Verdana, sans-serif'
            }
            },

                }]

            })
        })
    }

    $.getJSON('/_get_dates', {}, function(data) {
        dates = data.dates;
        timestamp = get_url_parameter('timestamp');
        tag_name = get_url_parameter('tag');
        cnt = find_current_timestamp(dates, timestamp);
        plot_statistics(tag_name);
        plot_salary_histogram(tag_name, dates[cnt]);
        print_plot_info(cnt, dates);
    });

    $('.earlier').bind('click', function() {
        if (cnt + 1 < dates.length) {
            cnt++;
        }
        print_plot_info(cnt, dates);
        plot_salary_histogram(tag_name, dates[cnt]);
    });
    $('.later').bind('click', function() {
        if (cnt - 1 >= 0) {
            cnt--;
        }
        print_plot_info(cnt, dates);
        plot_salary_histogram(tag_name, dates[cnt]);
    });


});
