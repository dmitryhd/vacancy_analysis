$(function() {
    var cnt = 0;
    var pics = [];
    $.getJSON('/_get_plots', {}, function(data) {
        pics = data.images;
    });
    $(".gallery_picture").attr("src", pics[cnt]);
    plot_statistics(pics[cnt]);
    $('#cnt').text(cnt);
    $('#plot_name').text(pics[cnt]);

    d_categories = [''];
    d_values = [0];
    function plot_statistics(plot_name) {
        $.getJSON('/_get_plot_data', {
            plot: plot_name
        }, function(data) {
            d_categories = data.d_categories;
            d_values = data.d_values;
            $('#container').highcharts({
                chart: {
                    type: 'bar'
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
