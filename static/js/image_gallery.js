$(function() {
    var cnt = 0;
    var pics = [];
    d_categories = [''];
    d_values = [0];

    $.getJSON('/_get_plots', {}, function(data) {
        pics = data.images;
        $(".gallery_picture").attr("src", pics[cnt]);
        plot_statistics(pics[cnt]);
        $('#cnt').text(cnt);
        $('#plot_name').text(pics[cnt]);
    });

    function plot_statistics(plot_name) {
        $.getJSON('/_get_statistics', {
            plot: plot_name,
            ask: 'vac_num'
        }, function(data) {
            d_categories = data.d_categories;
            d_values = data.d_values;
            $('#vac_number_container').highcharts({
                chart: {
                    type: 'bar'
                },
                plotOptions: {
                    series: {
                        animation: {
                            duration: 100
                        }
                    }
                },
                title: {
                    text: 'Количество вакансий по языку'
                },
                xAxis: {
                    categories: d_categories
                },
                yAxis: {
                    title: {
                        text: 'Количество вакансий по языку'
                    }
                },
                series: [{
                    name: 'Число вакансий',
                    data: d_values
                }]
            });
        })
        $.getJSON('/_get_statistics', {
            plot: plot_name,
            ask: 'vac_sal'
        }, function(data) {
            d_categories = data.categories;
            mean_max_salary = data.mean_max_salary;
            mean_min_salary = data.mean_min_salary;
            $('#vac_salary_container').highcharts({
                chart: {
                    type: 'bar'
                },
                plotOptions: {
                    series: {
                        animation: {
                            duration: 100
                        }
                    }
                },
                title: {
                    text: 'Зарплата'
                },
                xAxis: {
                    categories: d_categories
                },
                yAxis: {
                    title: {
                        text: 'Количество вакансий по языку'
                    }
                },
                series: [
                {
                    name: 'Минимальная зп. (средняя)',
                    data: mean_min_salary
                },
                {
                    name: 'Максимальная зп. (средняя)',
                    data: mean_max_salary
                }]
            });
        })
    }

    $('.earlier').bind('click', function() {
        $(".gallery_picture").attr("src", pics[cnt]);
        plot_statistics(pics[cnt]);
        $('#cnt').text(cnt);
        $('#plot_name').text(pics[cnt]);
        if (cnt + 1 < pics.length) {
            cnt++;
        }
    });
    $('.later').bind('click', function() {
        $(".gallery_picture").attr("src", pics[cnt]);
        plot_statistics(pics[cnt]);
        $('#cnt').text(cnt);
        $('#plot_name').text(pics[cnt]);
        if (cnt - 1 >= 0) {
            cnt--;
        }
    });

});
