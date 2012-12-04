jQuery(function($){
$(document).ready(function(){
	
    _ = jarn.i18n.MessageFactory('bika');
    PMF = jarn.i18n.MessageFactory('plone');

    function lookups(){
    	
        // Case Aetiologic Agents > Aetiologic Agent popup
        $(".template-caseaetiologicagents #Title").combogrid({
            colModel: [{'columnName':'Title', 'width':'25', 'label':_('Title')},
                       {'columnName':'Description', 'width':'65', 'label':_('Description')},
                       {'columnName':'AgentUID', 'hidden':true}],
            showOn: true,
            url: window.portal_url + "/getAetiologicAgents?_authenticator=" + $('input[name="_authenticator"]').val(),
            showOn: true,
            select: function( event, ui ) {
                event.preventDefault();
                $(this).val(ui.item.Title);
                $(this).parents('tr').find('input[id=Title]').val(ui.item.Title);
                $(this).parents('tr').find('input[id=Description]').val(ui.item.Description);
                $(this).parents('tr').find('input[id=AgentUID]').val(ui.item.AgentUID);
                //$(".template-caseaetiologicagents #Subtype").combogrid.url+=("&auid=" + ui.item.AgentUID);
                
                // Case Aetiologic Agents > Aetiologic agent row > Subtypes popup
                // This combo depends on the selected Aetiologic agent in the previous one
                $(".template-caseaetiologicagents #Subtype").combogrid({
                	colModel: [{'columnName':'Subtype', 'width':'25', 'label':_('Subtype')},
                               {'columnName':'SubtypeRemarks', 'width':'65', 'label':_('SubtypeRemarks')}],
                    showOn: true,
                    url: window.portal_url + "/getAetiologicAgentSubtypes?_authenticator=" + $('input[name="_authenticator"]').val()+"&auid=" + ui.item.AgentUID,
                    select: function( event, ui ) {
                        event.preventDefault();
                        $(this).val(ui.item.Subtype);
                        $(this).parents('tr').find('input[id=Subtype]').val(ui.item.Subtype);
                        $(this).change();
                        return false;
                    }
                });
                
                $(this).change();
                return false;
            }
        });
        
        $(".template-caseaetiologicagents #Title").change(function(event){
        	$.ajax({
                type: 'POST',
                url: window.portal_url + '/getAetiologicAgents',
                data: {'_authenticator': $('input[name="_authenticator"]').val(),
                       'title': $(this).val()},
        		dataType: "json",
	        	success: function(data, textStatus, $XHR){   
	        		if (data == null || data['rows'].length < 1) {
	        			//Aetiologic agent doesn't exist
	        			$(".template-caseaetiologicagents #Subtype").val('');
	        			$(".template-caseaetiologicagents #Title").val('');
	        			$(".template-caseaetiologicagents #Title").focus();
	        			$(".template-caseaetiologicagents #Subtype").attr('readonly', true);
	        		} else {
	        			$(".template-caseaetiologicagents #Subtype").focus();
	        			$(".template-caseaetiologicagents #Subtype").attr('readonly', false);
	        		}	        		
				},
				error: function(){
					//Error while searching for aetiologic agent
        			$(".template-caseaetiologicagents #Title").val('');
        			$(".template-caseaetiologicagents #Subtype").val('');
        			$(".template-caseaetiologicagents #Title").focus();
        			$(".template-caseaetiologicagents #Subtype").attr('readonly', true);
				}
            });
        });
        
        $(".template-caseaetiologicagents #Subtype").change(function(event){
        	$.ajax({
                type: 'POST',
                url: window.portal_url + '/getAetiologicAgentSubtypes',
                data: {'_authenticator': $('input[name="_authenticator"]').val(),
                       'title': $(this).val(),
                       'auid':$(".template-caseaetiologicagents #AgentUID").val()},
        		dataType: "json",
	        	success: function(data, textStatus, $XHR){   
	        		if (data == null || data['rows'].length < 1) {
	        			//Subtype doesn't exist
	        			$(".template-caseaetiologicagents #Subtype").val('');
	        			$(".template-caseaetiologicagents #Subtype").focus();
	        			$(".template-caseaetiologicagents .add_row").attr('disabled', 'disabled')
	        			return false;
	        		} else {
	        			$(".template-caseaetiologicagents .add_row").attr('disabled', '')
	        		}        		
				},
				error: function(){
					//Error while searching
        			$(".template-caseaetiologicagents #Subtype").val('');
        			$(".template-caseaetiologicagents #Subtype").focus();
        			$(".template-caseaetiologicagents .add_row").attr('disabled', '')
        			return false;
				}
            });
        });
    }
    lookups();

    $(".template-caseaetiologicagents .add_row").click(function(event){
        event.preventDefault();
        T = $(".template-caseaetiologicagents #Title").val();
        D = $(".template-caseaetiologicagents #Description").val();
        S = $(".template-caseaetiologicagents #Subtype").val();
        I = $(".template-caseaetiologicagents #AgentUID").val();
        if (T == '' || S == ''){
            return false;
        }
        
        // Check if record has been already added
        titrows = $("input[name='CAE_STitle:list']");
        for(i=0; i<titrows.length; i++){
        	title = titrows[i];
        	if (T==title.value) {
        		str=$("input[name='CAE_SSubtype:list']")[i];
        		if (str.value==S) {
        			alert(_('Aetiologic agent already added'));
        			$(".template-caseaetiologicagents #Subtype").val('');
        			$(".template-caseaetiologicagents #Subtype").focus();
        			return false;
        		}
        	}
		}
        titrows = $("input[name='CAE_Title:list']");
        for(i=0; i<titrows.length; i++){
        	title = titrows[i];
        	if (T==title.value) {
        		str=$("input[name='CAE_Subtype:list']")[i];
        		if (str.value==S) {
        			alert(_('Aetiologic agent already added'));
        			$(".template-caseaetiologicagents #Subtype").val('');
        			$(".template-caseaetiologicagents #Subtype").focus();
        			return false;
        		}
        	}
		}
        
        newrow = $(".template-caseaetiologicagents tr#new").clone();
        $(".template-caseaetiologicagents tr#new").removeAttr('id');
        $(".template-caseaetiologicagents #Title").parent().append("<span>"+T+"</span>");
        $(".template-caseaetiologicagents #Title").parent().append("<input type='hidden' name='CAE_Title:list' value='"+T+"'/>");
        $(".template-caseaetiologicagents #Title").remove();
        $(".template-caseaetiologicagents #AgentUID").parent().append("<input type='hidden' name='CAE_AgentUID:list' value='"+I+"'/>");
        $(".template-caseaetiologicagents #AgentUID").remove();
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
