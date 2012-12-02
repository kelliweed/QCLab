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
            showOn: true,
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
        C = $(".template-symptoms #Code").val();
        T = $(".template-symptoms #Title").val();
        D = $(".template-symptoms #Description").val();
        O = $(".template-symptoms #SymptomOnset").val();
        if (T == ''){
            return false;
        }

        // Avoids datewidget unload after adding new row without postback
        $(".template-symptoms #Onset").attr('class', 'datepicker_nofuture');

        newrow = $(".template-symptoms tr#new").clone();
        $(".template-symptoms tr#new").removeAttr('id');
        $(".template-symptoms #Code").parent().append("<span>"+C+"</span>");
        $(".template-symptoms #Code").parent().append("<input type='hidden' name='CSY_Code:list' value='"+C+"'/>");
        $(".template-symptoms #Code").remove();
        $(".template-symptoms #Title").parent().append("<span>"+T+"</span>");
        $(".template-symptoms #Title").parent().append("<input type='hidden' name='CSY_Title:list' value='"+T+"'/>");
        $(".template-symptoms #Title").remove();
        $(".template-symptoms #Description").parent().append("<span>"+D+"</span>");
        $(".template-symptoms #Description").parent().append("<input type='hidden' name='CSY_Description:list' value='"+D+"'/>");
        $(".template-symptoms #Description").remove();
        $(".template-symptoms #SymptomOnset").parent().append("<span>"+O+"</span>");
        $(".template-symptoms #SymptomOnset").parent().append("<input type='hidden' name='CSY_Onset:list' value='"+O+"'/>");
        $(".template-symptoms #SymptomOnset").remove();
        for(i=0; i<$(newrow).children().length; i++){
            td = $(newrow).children()[i];
            input = $(td).children()[0];
            $(input).val('');
        }
        $(newrow).appendTo($(".template-symptoms .bika-listing-table"));
        lookups();
        return false;
    })

});
});
