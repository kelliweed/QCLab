jQuery(function($){
$(document).ready(function(){

    _ = jarn.i18n.MessageFactory('bika');
    PMF = jarn.i18n.MessageFactory('plone');

    // Case Symptoms -> combined ICD9(R)/bika_symptoms lookup
    function lookups(){
        $(".template-symptoms #Title").combogrid({
            colModel: [{'columnName':'Code', 'width':'10', 'label':_('Code')},
                       {'columnName':'Title', 'width':'25', 'label':_('Title')},
                       {'columnName':'Description', 'width':'65', 'label':_('Description')}],
            url: window.portal_url + "/getSymptoms?_authenticator=" + $('input[name="_authenticator"]').val(),
            select: function( event, ui ) {
                event.preventDefault();
                $(this).val(ui.item.Title);
                $(this).parents('tr').find('input[id=Code]').val(ui.item.Code);
                $(this).parents('tr').find('input[id=Description]').val(ui.item.Description);
                $(this).change();
                return false;
            }
        });
    }
    lookups();

    $(".template-symptoms .add_row").click(function(event){
        event.preventDefault();
        C = $("#Code").val();
        T = $("#Title").val();
        D = $("#Description").val();
        O = $("#Onset").val();
        if (T == ''){
            return false;
        }

        // Avoids datewidget unload after adding new row without postback
        $("#Onset").attr('class', 'datepicker_nofuture');

        newrow = $("tr#new").clone();
        $("tr#new").removeAttr('id');
        $("#Code").parent().append("<span>"+C+"</span>");
        $("#Code").parent().append("<input type='hidden' name='CSY_Code:list' value='"+C+"'/>");
        $("#Code").remove();
        $("#Title").parent().append("<span>"+T+"</span>");
        $("#Title").parent().append("<input type='hidden' name='CSY_Title:list' value='"+T+"'/>");
        $("#Title").remove();
        $("#Description").parent().append("<span>"+D+"</span>");
        $("#Description").parent().append("<input type='hidden' name='CSY_Description:list' value='"+D+"'/>");
        $("#Description").remove();
        $("#Onset").parent().append("<span>"+O+"</span>");
        $("#Onset").parent().append("<input type='hidden' name='CSY_Onset:list' value='"+O+"'/>");
        $("#Onset").remove();
        for(i=0; i<$(newrow).children().length; i++){
            td = $(newrow).children()[i];
            input = $(td).children()[0];
            $(input).val('');
        }
        $(newrow).appendTo($(".bika-listing-table"));
        lookups();
        return false;
    })

});
});
