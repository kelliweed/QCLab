(function( $ ) {
$(document).ready(function(){

	_ = window.jsi18n_bika;
	PMF = window.jsi18n_plone;

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
