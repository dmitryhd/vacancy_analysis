var cnt = 0;
var pics = [];
$.getJSON('/_get_plots', {}, function(data) {
    pics = data.images;
});

var d_categories = [];
var d_from = [];
var d_to = [];


$(function() {
  $('.earlier').bind('click', function() {
      $(".gallery_picture").attr("src", pics[cnt]);
      if (cnt + 1 < pics.length) {
          cnt++;
      }
  });
  $('.later').bind('click', function() {
      $(".gallery_picture").attr("src", pics[cnt]);
      if (cnt - 1 >= 0) {
          cnt--;
      }
    $.getJSON('/_get_plot_data', {}, function(data) {
        d_categories = data.d_categories;
        d_from = data.d_from;
        d_to = data.d_to;
    });
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
            name: 'От',
            data: d_from
        }, {
            name: 'До',
            data: d_to
        }]
    });
  });

});
