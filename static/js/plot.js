var d_categories = [];
var d_from = [];
var d_to = [];

$.getJSON('/_get_plot_data', {}, function(data) {
    d_categories = data.d_categories;
    d_from = data.d_from;
    d_to = data.d_to;
});

var pics2 = [];
$.getJSON('/_get_plots', {}, function(data) {
  pics2 = data.images;
});

$(function () { 
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
