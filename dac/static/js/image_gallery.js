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

    $.getJSON('/_get_dates', {}, function(data) {
        dates = data.dates;
        timestamp = get_url_parameter('timestamp');
        cnt = find_current_timestamp(dates, timestamp);
        plot_statistics(dates[cnt]);
        print_plot_info(cnt, dates);
    });


    function plot_statistics(given_date) {
        $.getJSON('/_get_date_statistics', {
            date: given_date,
            ask: 'vac_num'
        }, function(data) {
            $('#vac_number_container').highcharts({
                chart: { type: 'bar'},
                plotOptions: {
                    series: {animation: {duration: 100}}
                },
                title: {text: 'Количество вакансий по языку'},
                xAxis: {categories: data.vac_num_categories },
                yAxis: {title: {text: 'Количество вакансий по языку'}},
                series: [{
                    name: 'Число вакансий',
                    data: data.vacancy_number
                }]
            });
            $('#vac_salary_container').highcharts({
                chart: { type: 'bar' },
                plotOptions: { series: { animation: { duration: 100 } } },
                title: { text: 'Зарплата' },
                xAxis: { categories: data.sal_categories },
                yAxis: { title: { text: 'Количество вакансий по языку' } },
                series: [{
                    name: 'Минимальная зп. (средняя)',
                    data: data.mean_min_salary
                    }, {
                    name: 'Максимальная зп. (средняя)',
                    data: data.mean_max_salary
                }]
            });
        })
    }

    $('.earlier').bind('click', function() {
        if (cnt + 1 < dates.length) {
            cnt++;
        }
        plot_statistics(dates[cnt]);
        print_plot_info(cnt, dates);
    });
    $('.later').bind('click', function() {
        if (cnt - 1 >= 0) {
            cnt--;
        }
        plot_statistics(dates[cnt]);
        print_plot_info(cnt, dates);
    });

});
