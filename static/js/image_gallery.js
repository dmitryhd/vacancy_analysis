var cnt = 0;
var pics = [];
$.getJSON('/_get_plots', {}, function(data) {
    pics = data.images;
});

d_categories = ['yy'];
d_from = [12];
d_to = [];


$(function() {
  $('.earlier').bind('click', function() {
      $(".gallery_picture").attr("src", pics[cnt]);
      if (cnt + 1 < pics.length) {
          cnt++;
      }
  });
  $('.later').bind('click', function() {
    $.getJSON('/_get_plot_data', {plot: 1417618752}, function(data) {
        d_categories = data.d_categories;
        d_from = data.d_from;
        d_to = data.d_to;
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
            data: d_from
        } ]
    });
    })
      $(".gallery_picture").attr("src", pics[cnt]);
      if (cnt - 1 >= 0) {
          cnt--;
      }
  });

});
