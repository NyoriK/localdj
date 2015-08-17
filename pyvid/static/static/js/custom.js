$(document).ready(function(){
    var lastTopPosition = 0;
    $(window).scroll(function(){
        var topPosition = $(window).scrollTop();
        if (topPosition > lastTopPosition ){
            $("#navbar_header").stop(true).animate({'top':'-40px'}, 200);
            $("#navbar_footer").stop(true).animate({'bottom':'-40px'}, 200);
        } else {
            $("#navbar_header").stop(true).animate({'top':'0px'}, 200);
            $("#navbar_footer").stop(true).animate({'bottom':'0px'}, 200);
        }
        lastTopPosition = topPosition;
    });
    
    $('.video-info').click(function(){
        $(this).closest('.video-wrapper').children('.video-description').fadeToggle();
    });
});