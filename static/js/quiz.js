var running = false;
var selected = false;
function unselect() {
    selected = false;
    $(".answer").each(function (i, v) {
        $(v).find('.ansletter').removeClass("permahighlight");
        $(v).children().each(function (i, k) {
            $(k).removeClass("selected");
            $(k).removeClass("correct");
            $(k).removeClass("correctchoise");
            $(k).removeClass("wrong");
        });
    });
};
