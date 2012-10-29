(function( $ ) {
$(document).ready(function(){

	_ = window.jsi18n_bika;
	PMF = window.jsi18n_plone;

    // Add Patient popup
    if(window.location.href.search('portal_factory/Patient') == -1){
        $("input[id=PatientID]").after('<a style="border-bottom:none !important;margin-left:.5;"' +
                    ' class="add_patient"' +
                    ' href="'+window.portal_url+'/patients/portal_factory/Patient/new/edit"' +
                    ' rel="#overlay">' +
                    ' <img style="padding-bottom:1px;" src="'+window.portal_url+'/++resource++bika.lims.images/add.png"/>' +
                ' </a>');
    }
    $('a.add_patient').prepOverlay(
        {
            subtype: 'ajax',
            filter: 'head>*,#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
            formselector: '#patient-base-edit',
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

	// Estimate DOB if an age is typed
	$("#Age").live('change', function(){
		if (parseInt($(this).val()) > 0){
			var d = new Date();
			year = d.getFullYear() - $(this).val();
			var dob = year + "-01-01";
			$("#BirthDate").val(dob);
			$("#BirthDateEstimated").attr('checked', true);
		}
		else {
			$("#BirthDate").val("");
			$("#BirthDateEstimated").attr('checked', false);
		}
	})

	// Mod the Age if DOB is selected
	$("#BirthDate").live('change', function(){
		var dob = new Date($(this).val());
		if (dob!= undefined && dob != null){
			var now = new Date();
			var one_year = 86400 * 365 * 1000
			var age = ((now.getTime()-dob.getTime())/one_year).toString().split(".")[0];
			if (age == undefined || age == 'NaN') {
				$("#Age").val("");
			} else {
				$("#Age").val(age);
			}
		}
		else {
			$("#Age").val("");
		}
		$("#BirthDateEstimated").attr('checked', false);
	});

	function lookups(){
		// Treatment History Treatment search popup
		$(".template-treatmenthistory #Treatment").combogrid({
			colModel: [{'columnName':'Type', 'width':'50', 'label':window.jsi18n_bika('Type')},
			           {'columnName':'Title', 'width':'50', 'label':window.jsi18n_bika('Title')}],
			url: window.location.href.replace("/treatmenthistory","") + "/getTreatments?_authenticator=" + $('input[name="_authenticator"]').val(),
			select: function( event, ui ) {
				event.preventDefault();
				$(this).val(ui.item.Title);
				$(this).change();
				return false;
			}
		});

		// Treatment History Drug search popup
		$(".template-treatmenthistory #Drug").combogrid({
			colModel: [{'columnName':'Title', 'width':'50', 'label':window.jsi18n_bika('Title')}],
			url: window.location.href.replace("/treatmenthistory","") + "/getDrugs?_authenticator=" + $('input[name="_authenticator"]').val(),
			select: function( event, ui ) {
				event.preventDefault();
				$(this).val(ui.item.Title);
				$(this).change();
				return false;
			}
		});

		// Allergies > Prohibited Drug Explanations search popup
		$(".template-allergies #DrugProhibition").combogrid({
			colModel: [{'columnName':'Title', 'width':'50', 'label':window.jsi18n_bika('Title')}],
			url: window.location.href.replace("/allergies","") + "/getDrugProhibitions?_authenticator=" + $('input[name="_authenticator"]').val(),
			select: function( event, ui ) {
				event.preventDefault();
				$(this).val(ui.item.Title);
				$(this).change();
				return false;
			}
		});

		// Allergies > Drug search popup
		$(".template-allergies #Drug").combogrid({
			colModel: [{'columnName':'Title', 'width':'50', 'label':window.jsi18n_bika('Title')}],
			url: window.location.href.replace("/allergies","") + "/getDrugs?_authenticator=" + $('input[name="_authenticator"]').val(),
			select: function( event, ui ) {
				event.preventDefault();
				$(this).val(ui.item.Title);
				$(this).change();
				return false;
			}
		});

		// Immunization History > Immunization search popup
		$(".template-immunizationhistory #Immunization").combogrid({
			colModel: [{'columnName':'Title', 'width':'50', 'label':window.jsi18n_bika('Title')}],
			url: window.location.href.replace("/immunizationhistory","") + "/getImmunizations?_authenticator=" + $('input[name="_authenticator"]').val(),
			select: function( event, ui ) {
				event.preventDefault();
				$(this).val(ui.item.Title);
				$(this).change();
				return false;
			}
		});

		// Immunization History > VaccionationCenter search popup
		$(".template-immunizationhistory #VaccinationCenter").combogrid({
			colModel: [{'columnName':'Title', 'width':'50', 'label':window.jsi18n_bika('Title')}],
			url: window.location.href.replace("/immunizationhistory","") + "/getVaccinationCenters?_authenticator=" + $('input[name="_authenticator"]').val(),
			select: function( event, ui ) {
				event.preventDefault();
				$(this).val(ui.item.Title);
				$(this).change();
				return false;
			}
		});

		// Chronic Conditions -> combined ICD9(R)/bika_symptoms lookup
		$(".template-chronicconditions #Title").combogrid({
			colModel: [{'columnName':'Code', 'width':'10', 'label':window.jsi18n_bika('Code')},
			           {'columnName':'Title', 'width':'25', 'label':window.jsi18n_bika('Title')},
			           {'columnName':'Description', 'width':'65', 'label':window.jsi18n_bika('Description')}],
			url: window.location.href.replace("/chronicconditions","") + "/getSymptoms?_authenticator=" + $('input[name="_authenticator"]').val(),
			select: function( event, ui ) {
				event.preventDefault();
				$(this).val(ui.item.Title);
				$(this).parents('tr').find('input[id=Code]').val(ui.item.Code);
				$(this).parents('tr').find('input[id=Description]').val(ui.item.Description);
				$(this).change();
				return false;
			}
		});

		// Travel History > Countries search popup
		$(".template-travelhistory #Country").combogrid({
			colModel: [{'columnName':'Code', 'width':'10', 'label':window.jsi18n_bika('Code')},
			           {'columnName':'Country', 'width':'25', 'label':window.jsi18n_bika('Country')}],
			url: window.location.href.replace("/travelhistory","") + "/getCountries?_authenticator=" + $('input[name="_authenticator"]').val(),
			select: function( event, ui ) {
				event.preventDefault();
				$(this).val(ui.item.Title);
				$(this).parents('tr').find('input[id=Country]').val(ui.item.Country);
				$(this).change();
				return false;
			}
		});
    }
	lookups();

	$(".template-treatmenthistory .add_row").click(function(event){
		event.preventDefault();
		T = $("#Treatment").val();
		D = $("#Drug").val();
		S = $("#Start").val();
		E = $("#End").val();
		if (T == '' || D == ''){
	        return false;
		}
		newrow = $("tr#new").clone();
        $("tr#new").removeAttr('id');
		$("#Treatment").parent().append("<span>"+T+"</span>");
		$("#Treatment").parent().append("<input type='hidden' name='Treatment:list' value='"+T+"'/>");
		$("#Treatment").remove();
		$("#Drug").parent().append("<span>"+D+"</span>");
		$("#Drug").parent().append("<input type='hidden' name='Drug:list' value='"+D+"'/>");
		$("#Drug").remove();
		$("#Start").parent().append("<span>"+S+"</span>");
		$("#Start").parent().append("<input type='hidden' name='Start:list' value='"+S+"'/>");
		$("#Start").remove();
		$("#End").parent().append("<span>"+E+"</span>");
		$("#End").parent().append("<input type='hidden' name='End:list' value='"+E+"'/>");
		$("#End").remove();
		for(i=0; i<$(newrow).children().length; i++){
            td = $(newrow).children()[i];
            input = $(td).children()[0];
            $(input).val('');
        }
        $(newrow).appendTo($(".bika-listing-table"));
        lookups();
        return false;
	})

	$(".template-allergies .add_row").click(function(event){
		event.preventDefault();
		P = $("#DrugProhibition").val();
		D = $("#Drug").val();
		if (P == '' || D == ''){
	        return false;
		}
		newrow = $("tr#new").clone();
        $("tr#new").removeAttr('id');
		$("#DrugProhibition").parent().append("<span>"+P+"</span>");
		$("#DrugProhibition").parent().append("<input type='hidden' name='DrugProhibition:list' value='"+P+"'/>");
		$("#DrugProhibition").remove();
		$("#Drug").parent().append("<span>"+D+"</span>");
		$("#Drug").parent().append("<input type='hidden' name='Drug:list' value='"+D+"'/>");
		$("#Drug").remove();
		for(i=0; i<$(newrow).children().length; i++){
            td = $(newrow).children()[i];
            input = $(td).children()[0];
            $(input).val('');
        }
        $(newrow).appendTo($(".bika-listing-table"));
        lookups();
        return false;
	})

	$(".template-immunizationhistory .add_row").click(function(event){
		event.preventDefault();
		I = $("#Immunization").val();
		V = $("#VaccinationCenter").val();
		D = $("#Date").val();
		if (I == '' || V == ''){
	        return false;
		}
		newrow = $("tr#new").clone();
        $("tr#new").removeAttr('id');
		$("#Immunization").parent().append("<span>"+I+"</span>");
		$("#Immunization").parent().append("<input type='hidden' name='Immunization:list' value='"+I+"'/>");
		$("#Immunization").remove();
		$("#VaccinationCenter").parent().append("<span>"+V+"</span>");
		$("#VaccinationCenter").parent().append("<input type='hidden' name='VaccinationCenter:list' value='"+V+"'/>");
		$("#VaccinationCenter").remove();
		$("#Date").parent().append("<span>"+D+"</span>");
		$("#Date").parent().append("<input type='hidden' name='Date:list' value='"+D+"'/>");
		$("#Date").remove();
		for(i=0; i<$(newrow).children().length; i++){
            td = $(newrow).children()[i];
            input = $(td).children()[0];
            $(input).val('');
        }
        $(newrow).appendTo($(".bika-listing-table"));
        lookups();
        return false;
	})

	$(".template-chronicconditions .add_row").click(function(event){
		event.preventDefault();
		C = $("#Code").val();
		T = $("#Title").val();
		D = $("#Description").val();
		O = $("#Onset").val();
		R = $("#Remarks").val();
		if (T == ''){
	        return false;
		}
		newrow = $("tr#new").clone();
        $("tr#new").removeAttr('id');
		$("#Code").parent().append("<span>"+C+"</span>");
		$("#Code").parent().append("<input type='hidden' name='Code:list' value='"+C+"'/>");
		$("#Code").remove();
		$("#Title").parent().append("<span>"+T+"</span>");
		$("#Title").parent().append("<input type='hidden' name='Title:list' value='"+T+"'/>");
		$("#Title").remove();
		$("#Description").parent().append("<span>"+D+"</span>");
		$("#Description").parent().append("<input type='hidden' name='Description:list' value='"+D+"'/>");
		$("#Description").remove();
		$("#Onset").parent().append("<span>"+O+"</span>");
		$("#Onset").parent().append("<input type='hidden' name='Onset:list' value='"+O+"'/>");
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

	$(".template-travelhistory .add_row").click(function(event){
		event.preventDefault();
		S = $("#TripStartDate").val();
		E = $("#TripEndDate").val();
		T = $("#Country").val();
		L = $("#Location").val();
		if (T == ''){
	        return false;
		}
		newrow = $("tr#new").clone();
        $("tr#new").removeAttr('id');
		$("#TripStartDate").parent().append("<span>"+S+"</span>");
		$("#TripStartDate").parent().append("<input type='hidden' name='TripStartDate:list' value='"+S+"'/>");
		$("#TripStartDate").remove();
		$("#TripEndDate").parent().append("<span>"+E+"</span>");
		$("#TripEndDate").parent().append("<input type='hidden' name='TripEndDate:list' value='"+E+"'/>");
		$("#TripEndDate").remove();
		$("#Country").parent().append("<span>"+T+"</span>");
		$("#Country").parent().append("<input type='hidden' name='Country:list' value='"+T+"'/>");
		$("#Country").remove();
		$("#Location").parent().append("<span>"+L+"</span>");
		$("#Location").parent().append("<input type='hidden' name='Location:list' value='"+L+"'/>");
		$("#Location").remove();
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
}(jQuery));
