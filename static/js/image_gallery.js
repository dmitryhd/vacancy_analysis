var cnt = 0;
var pics = [];
$.getJSON('/_get_plots', {}, function(data) {
    pics = data.images;
});
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
    });
});
