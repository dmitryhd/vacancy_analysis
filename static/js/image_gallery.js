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

    $.getJSON('/_get_dates', {}, function(data) {
        dates = data.dates;
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
                xAxis: {categories: data.categories },
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
                xAxis: { categories: d_categories },
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
        plot_statistics(dates[cnt]);
        print_plot_info(cnt, dates);
        if (cnt + 1 < dates.length) {
            cnt++;
        }
    });
    $('.later').bind('click', function() {
        plot_statistics(dates[cnt]);
        print_plot_info(cnt, dates);
        if (cnt - 1 >= 0) {
            cnt--;
        }
    });

});
