(function( $ ) {
$(document).ready(function(){

	_ = window.jsi18n_bika;
	PMF = window.jsi18n_plone;

	// Estimate DOB if an age is typed
	$("#Age").change(function(){
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
	$("#BirthDate").change(function(){
		var dob = new Date($(this).val());
		if (dob!= undefined && dob != null){
			var now = new Date();
			var one_year = 86400 * 365 * 1000
			var age = ((now.getTime()-dob.getTime())/one_year).toString().split(".")[0];
			$("#Age").val(age);
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
	}
	lookups();

	$(".template-treatmenthistory .add_row").click(function(){
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
	
	$(".template-allergies .add_row").click(function(){
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


});
}(jQuery));
