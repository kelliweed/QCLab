jQuery(function($){
$(document).ready(function(){

    function lookups(){
    	
        // Case Aetiologic Agents > Aetiologic Agent popup
        $(".template-caseaetiologicagents #Title").combogrid({
            colModel: [{'columnName':'Title', 'width':'25', 'label':window.jsi18n_bika('Title')},
                       {'columnName':'Description', 'width':'65', 'label':window.jsi18n_bika('Description')},
                       {'columnName':'Subtype', 'width':'25', 'label':window.jsi18n_bika('Subtype')}],
            url: window.portal_url + "/getAetiologicAgents?_authenticator=" + $('input[name="_authenticator"]').val(),
            select: function( event, ui ) {
                event.preventDefault();
                $(this).val(ui.item.Title);
                $(this).parents('tr').find('input[id=Title]').val(ui.item.Title);
                $(this).parents('tr').find('input[id=Description').val(ui.item.Description)
                $(this).change();
                return false;
            }
        });
        
        // Case Aetiologic Agents > Aetiologic agent row > Subtypes popup
        $(".template-caseaetiologicagents #Subtype").combogrid({
        	colModel: [{'columnName':'Subtype', 'width':'25', 'label':window.jsi18n_bika('Subtype')},
                       {'columnName':'SubtypeRemarks', 'width':'65', 'label':window.jsi18n_bika('SubtypeRemarks')},
            url: window.portal_url + "/getAetiologicAgentSubtypes?_authenticator=" + $('input[name="_authenticator"]').val()
            					   + "&aetiologicagent=" + $(this).parents('tr').find('Title').val(),
            select: function( event, ui ) {
                event.preventDefault();
                $(this).val(ui.item.Title);
                $(this).change();
                return false;
            }
        });
    }
    lookups();

    $(".template-caseaetiologicagents .add_row").click(function(event){
        event.preventDefault();
        T = $("#Title").val();
        D = $("#Description").val();
        S = $("#Subtype").val();
        if (T == ''){
            return false;
        }
        
        newrow = $("tr#new").clone();
        $("tr#new").removeAttr('id');
        $("#Title").parent().append("<span>"+T+"</span>");
        $("#Title").parent().append("<input type='hidden' name='CAE_Title:list' value='"+T+"'/>");
        $("#Title").remove();
        $("#Description").parent().append("<span>"+D+"</span>");
        $("#Description").parent().append("<input type='hidden' name='CAE_Description:list' value='"+D+"'/>");
        $("#Description").remove();
        $("#Subtype").parent().append("<span>"+S+"</span>");
        $("#Subtype").parent().append("<input type='hidden' name='CAE_Subtype:list' value='"+S+"'/>");
        $("#Subtype").remove();
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
