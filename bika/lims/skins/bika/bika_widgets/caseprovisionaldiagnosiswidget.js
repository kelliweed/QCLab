jQuery(function($){
$(document).ready(function(){

    _ = jarn.i18n.MessageFactory('bika');
    PMF = jarn.i18n.MessageFactory('plone');

    // Case Symptoms -> combined ICD9(R)/bika_symptoms lookup
    function lookups(){
        $(".template-caseprovisionaldiagnosis #Title").combogrid({
            colModel: [{'columnName':'Code', 'width':'10', 'label':_('Code')},
                       {'columnName':'Title', 'width':'25', 'label':_('Title')},
                       {'columnName':'Description', 'width':'65', 'label':_('Description')}],
            url: window.portal_url + "/getSymptoms?r_only=0&_authenticator=" + $('input[name="_authenticator"]').val(),
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

    $(".template-caseprovisionaldiagnosis .add_row").click(function(event){
        event.preventDefault();
        C = $(".template-caseprovisionaldiagnosis #Code").val();
        T = $(".template-caseprovisionaldiagnosis #Title").val();
        D = $(".template-caseprovisionaldiagnosis #Description").val();
        O = $(".template-caseprovisionaldiagnosis #Onset").val();
        if (T == ''){
            return false;
        }

        // Avoids datewidget unload after adding new row without postback
        $(".template-caseprovisionaldiagnosis #Onset").attr('class', 'datepicker_nofuture');

        newrow = $(".template-caseprovisionaldiagnosis tr#new").clone();
        $(".template-caseprovisionaldiagnosis tr#new").removeAttr('id');
        $(".template-caseprovisionaldiagnosis #Code").parent().append("<span>"+C+"</span>");
        $(".template-caseprovisionaldiagnosis #Code").parent().append("<input type='hidden' name='CPD_Code:list' value='"+C+"'/>");
        $(".template-caseprovisionaldiagnosis #Code").remove();
        $(".template-caseprovisionaldiagnosis #Title").parent().append("<span>"+T+"</span>");
        $(".template-caseprovisionaldiagnosis #Title").parent().append("<input type='hidden' name='CPD_Title:list' value='"+T+"'/>");
        $(".template-caseprovisionaldiagnosis #Title").remove();
        $(".template-caseprovisionaldiagnosis #Description").parent().append("<span>"+D+"</span>");
        $(".template-caseprovisionaldiagnosis #Description").parent().append("<input type='hidden' name='CPD_Description:list' value='"+D+"'/>");
        $(".template-caseprovisionaldiagnosis #Description").remove();
        $(".template-caseprovisionaldiagnosis #Onset").parent().append("<span>"+O+"</span>");
        $(".template-caseprovisionaldiagnosis #Onset").parent().append("<input type='hidden' name='CPD_Onset:list' value='"+O+"'/>");
        $(".template-caseprovisionaldiagnosis #Onset").remove();
        for(i=0; i<$(newrow).children().length; i++){
            td = $(newrow).children()[i];
            input = $(td).children()[0];
            $(input).val('');
        }
        $(newrow).appendTo($(".template-caseprovisionaldiagnosis .bika-listing-table"));
        lookups();
        return false;
    })

});
});
