(function( $ ) {
$(document).ready(function(){

    _ = jarn.i18n.MessageFactory('bika');
    PMF = jarn.i18n.MessageFactory('plone');

     if($(".portaltype-batch").length == 0 &&
       window.location.href.search('portal_factory/Batch') == -1){
        $("input[id=BatchID]").after('<a style="border-bottom:none !important;margin-left:.5;"' +
                    ' class="add_batch"' +
                    ' href="'+window.portal_url+'/batches/portal_factory/Batch/new/edit"' +
                    ' rel="#overlay">' +
                    ' <img style="padding-bottom:1px;" src="'+window.portal_url+'/++resource++bika.lims.images/add.png"/>' +
                ' </a>');
        ajax_url = window.location.href.replace("/ar_add","")
                 + "/getBatches?_authenticator=" + $('input[name="_authenticator"]').val();
        if ($("#ar_0_PatientUID").length > 0) {
            ajax_url = ajax_url + "&PatientUID=" + $("#ar_0_PatientUID").val();
        }
        if ($("#ar_0_ClientUID").length > 0) {
            ajax_url = ajax_url + "&ClientUID=" + $("#ar_0_ClientUID").val();
        }
        $("input[id*=BatchID]").combogrid({
            width: "650px",
            colModel: [{'columnName':'BatchUID','hidden':true},
                       {'columnName':'BatchID','width':'10','label':_('Batch ID')},
                       {'columnName':'PatientTitle','width':'30','label':_('Patient')},
                       {'columnName':'DoctorTitle','width':'30','label':_('Doctor')},
                       {'columnName':'ClientTitle','width':'30','label':_('Hospital')}],
            url: ajax_url,
            select: function( event, ui ) {
                if (window.location.href.search('ar_add') > -1){  // epid ar_add
                    column = $(this).attr('name').split(".")[1];
                    if($('#ar_'+column+'_PatientID').length > 0){
                        $('#ar_'+column+'_PatientID').val(ui.item.PatientID);
                    }
                    if($('#ar_'+column+'_DoctorID').length > 0){
                        $('#ar_'+column+'_DoctorID').val(ui.item.DoctorID);
                    }
                    if($('#ar_'+column+'_ClientID').length > 0){
                        $('#ar_'+column+'_ClientID').val(ui.item.ClientID);
                    }
                }
                $(this).val(ui.item.BatchID);
                $(this).change();
                return false;
            }
        });
    }

    if($(".portaltype-batch").length > 0 && $(".template-base_edit").length > 0) {
        $.ajax({
            url: window.location.href
                       .split("?")[0]
                       .replace("/base_edit", "")
                       .replace("/edit", "") + "/getBatchInfo",
            type: 'POST',
            data: {'_authenticator': $('input[name="_authenticator"]').val()},
            dataType: "json",
            success: function(data, textStatus, $XHR){
                $(".jsClientTitle").remove();
                $("#archetypes-fieldname-ClientID").append("<span class='jsClientTitle'>"+data['Client']+"</span>");
                $(".jsPatientTitle").remove();
                $("#archetypes-fieldname-PatientID").append("<span class='jsPatientTitle'>"+data['Patient']+"</span>");
                $(".jsDoctorTitle").remove();
                $("#archetypes-fieldname-DoctorID").append("<span class='jsDoctorTitle'>"+data['Doctor']+"</span>");
            }
        });
    }


    $('a.add_batch').prepOverlay(
        {
            subtype: 'ajax',
            filter: 'head>*,#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
            formselector: '#batch-base-edit',
            closeselector: '[name="form.button.cancel"]',
            width:'70%',
            noform:'close',
            config: {
                onLoad: function() {
                    // manually remove remarks
                    this.getOverlay().find("#archetypes-fieldname-Remarks").remove();
//                  // display only first tab's fields
//                  $("ul.formTabs").remove();
//                  $("#fieldset-schemaname").remove();
                },
                onClose: function(){
                    // here is where we'd populate the form controls, if we cared to.
                }
            }
        }
    );


});
}(jQuery));
