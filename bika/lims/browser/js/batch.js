(function( $ ) {
$(document).ready(function(){

    _ = window.jsi18n_bika;
    PMF = window.jsi18n_plone;

    // This is *not* a lookup in batch context.
    if(!(window.location.href.search('batches'))){
        $("input[id*=BatchID]").combogrid({
            colModel: [{'columnName':'BatchUID','hidden':true},
                       {'columnName':'BatchID','width':'25','label':window.jsi18n_bika('Batch ID')},
                       {'columnName':'Description','width':'35','label':window.jsi18n_bika('Description')}],
            url: window.portal_url + "/getBatches?_authenticator=" + $('input[name="_authenticator"]').val(),
            select: function( event, ui ) {
                $(this).val(ui.item.BatchID);
                $(this).change();
                return false;
            }
        });
    }

    $("input[id*=ClientID]").combogrid({
        colModel: [{'columnName':'ClientUID','hidden':true},
                   {'columnName':'ClientID','width':'25','label':window.jsi18n_bika('Client ID')},
                   {'columnName':'Title','width':'35','label':window.jsi18n_bika('Title')}],
        url: window.portal_url + "/getClients?_authenticator=" + $('input[name="_authenticator"]').val(),
        select: function( event, ui ) {
            $(this).val(ui.item.ClientID);
            $(this).change();
            return false;
        }
    });

    $("input[id*=PatientID]").combogrid({
        colModel: [{'columnName':'PatientUID','hidden':true},
                   {'columnName':'PatientID','width':'25','label':window.jsi18n_bika('Patient ID')},
                   {'columnName':'Title','width':'35','label':window.jsi18n_bika('Title')}],
        url: window.portal_url + "/getPatients?_authenticator=" + $('input[name="_authenticator"]').val(),
        select: function( event, ui ) {
            $(this).val(ui.item.PatientID);
            // ui.item.PrimaryReferrer (title)
            $(this).change();
            return false;
        }
    });

    $("input[id*=Doctor]").combogrid({
        colModel: [{'columnName':'DoctorUID','hidden':true},
                   {'columnName':'Title','width':'35','label':window.jsi18n_bika('Title')}],
        url: window.portal_url + "/getDoctors?_authenticator=" + $('input[name="_authenticator"]').val(),
        select: function( event, ui ) {
            $(this).val(ui.item.Doctor);
            $(this).change();
            return false;
        }
    });

});
}(jQuery));
