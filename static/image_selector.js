var cnt = 0;
var pictures = {{images|safe}};
$(".to_left").click(function(){
    $(".gallery_picture").attr("src", pictures[cnt]);
    if (cnt < pictures.length) {
        cnt++;
    }
});
$(".to_right").click(function(){
    $(".gallery_picture").attr("src", pictures[cnt]);
    if (cnt >= 0) {
        cnt--;
    }
});
