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

	// Treatment History Drug search popup
	$("[field='Drug']").combogrid({
		colModel: [{'columnName':'Title', 'width':'50', 'label':window.jsi18n_bika('Title')}],
		url: window.location.href.replace("/treatmenthistory","") + "/getDrugs?_authenticator=" + $('input[name="_authenticator"]').val(),
		select: function( event, ui ) {
			$(this).val(ui.item.Title);
			$(this).change();
			return false;
		}
	});

});
}(jQuery));
