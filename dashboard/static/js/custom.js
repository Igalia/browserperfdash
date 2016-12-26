$( document ).ready( function() {
    $( "#reload" ).on( "click", function( e ) {
        var $icon = $( this ).find( ".glyphicon.glyphicon-refresh" ),
            animateClass = "glyphicon-refresh-animate";

        $icon.addClass( animateClass );
        // setTimeout is to indicate some async operation
        window.setTimeout( function() {
            $icon.removeClass( animateClass );
        }, 1000 );
    });
});