jQuery(function($){
$(document).ready(function(){
	
    _ = jarn.i18n.MessageFactory('bika');
    PMF = jarn.i18n.MessageFactory('plone');

    function lookups(){
    	
        // Case Aetiologic Agents > Aetiologic Agent popup
        $(".template-caseaetiologicagents #Title").combogrid({
            colModel: [{'columnName':'Title', 'width':'25', 'label':_('Title')},
                       {'columnName':'Description', 'width':'65', 'label':_('Description')},
                       {'columnName':'Subtype', 'width':'25', 'label':_('Subtype')}],
            url: window.portal_url + "/getAetiologicAgents?_authenticator=" + $('input[name="_authenticator"]').val(),
            select: function( event, ui ) {
                event.preventDefault();
                $(this).val(ui.item.Title);
                $(this).parents('tr').find('input[id=Title]').val(ui.item.Title);
                $(this).parents('tr').find('input[id=Description]').val(ui.item.Description)
                $(this).change();
                return false;
            }
        });
        
        // Case Aetiologic Agents > Aetiologic agent row > Subtypes popup
        $(".template-caseaetiologicagents #Subtype").combogrid({
        	colModel: [{'columnName':'Subtype', 'width':'25', 'label':_('Subtype')},
                       {'columnName':'SubtypeRemarks', 'width':'65', 'label':_('SubtypeRemarks')}],
            url: window.portal_url + "/getAetiologicAgentSubtypes?_authenticator=" + $('input[name="_authenticator"]').val(),
     //       						+"&aetiologicagent=" + $(this).parents('tr').find('input[id=Title]').val(),
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
        T = $(".template-caseaetiologicagents #Title").val();
        D = $(".template-caseaetiologicagents #Description").val();
        S = $(".template-caseaetiologicagents #Subtype").val();
        if (T == ''){
            return false;
        }
        
        newrow = $(".template-caseaetiologicagents tr#new").clone();
        $(".template-caseaetiologicagents tr#new").removeAttr('id');
        $(".template-caseaetiologicagents #Title").parent().append("<span>"+T+"</span>");
        $(".template-caseaetiologicagents #Title").parent().append("<input type='hidden' name='CAE_Title:list' value='"+T+"'/>");
        $(".template-caseaetiologicagents #Title").remove();
        $(".template-caseaetiologicagents #Description").parent().append("<span>"+D+"</span>");
        $(".template-caseaetiologicagents #Description").parent().append("<input type='hidden' name='CAE_Description:list' value='"+D+"'/>");
        $(".template-caseaetiologicagents #Description").remove();
        $(".template-caseaetiologicagents #Subtype").parent().append("<span>"+S+"</span>");
        $(".template-caseaetiologicagents #Subtype").parent().append("<input type='hidden' name='CAE_Subtype:list' value='"+S+"'/>");
        $(".template-caseaetiologicagents #Subtype").remove();
        for(i=0; i<$(newrow).children().length; i++){
            td = $(newrow).children()[i];
            input = $(td).children()[0];
            $(input).val('');
        }
        $(newrow).appendTo($(".template-caseaetiologicagents .bika-listing-table"));
        lookups();
        return false;
    })

});
});
