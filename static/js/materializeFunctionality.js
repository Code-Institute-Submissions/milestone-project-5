    //loads materializecss functionality 
    $(document).ready(function() {
        //required for select form
        $('select').formSelect().isMultiple;
        //required for sidenav
        $('.sidenav').sidenav();
        //required for form character limit
        $('input#input_text, textarea#blurb').characterCounter();
        $('#username').characterCounter();
        //required for collapsible
        $('.collapsible').collapsible();
        //requred for tabs:
        $('.tabs').tabs();
    });