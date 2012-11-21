(function( $ ) {
$(document).ready(function(){

    _ = jarn.i18n.MessageFactory('bika');
    PMF = jarn.i18n.MessageFactory('plone');

    if($(".portaltype-doctor").length == 0 &&
       window.location.href.search('portal_factory/Doctor') == -1){
        $("input[id=DoctorID]").after('<a style="border-bottom:none !important;margin-left:.5;"' +
                    ' class="add_doctor"' +
                    ' href="'+window.portal_url+'/doctors/portal_factory/Doctor/new/edit"' +
                    ' rel="#overlay">' +
                    ' <img style="padding-bottom:1px;" src="'+window.portal_url+'/++resource++bika.lims.images/add.png"/>' +
                ' </a>');
        $("input[id*=DoctorID]").combogrid({
            colModel: [{'columnName':'DoctorUID','hidden':true},
                       {'columnName':'DoctorID','width':'25','label':_('Doctor ID')},
                       {'columnName':'Title','width':'75','label':_('Title')}],
            url: window.portal_url + "/getDoctors?_authenticator=" + $('input[name="_authenticator"]').val(),
            select: function( event, ui ) {
                $(this).val(ui.item.DoctorID);
                $(this).change();
                if($(".portaltype-batch").length > 0 && $(".template-base_edit").length > 0) {
                    $(".jsDoctorTitle").remove();
                    $("#archetypes-fieldname-DoctorID").append("<span class='jsDoctorTitle'>"+ui.item.Title+"</span>");
                }
                return false;
            }
        });
    }
    // Add Doctor popup
    $('a.add_doctor').prepOverlay(
        {
            subtype: 'ajax',
            filter: 'head>*,#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
            formselector: '#doctor-base-edit',
            closeselector: '[name="form.button.cancel"]',
            width:'40%',
            noform:'close',
            config: {
            	onLoad: function() {
            		// manually remove remarks
            		this.getOverlay().find("#archetypes-fieldname-Remarks").remove();
	            }
            }
	    }
    );

});
}(jQuery));
