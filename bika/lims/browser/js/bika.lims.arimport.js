/**
 * Controller class for ARImport view
 */
function AnalysisRequestImportView() {

    var that = this;

    that.load = function() {

        // the ClientName string field should have a lookup
        $("input[id*='ClientName']").combogrid({
            colModel: [{'columnName':'ClientID','width':'20','label':_('Client ID')},
                       {'columnName':'Title','width':'80','label':_('Title')}],
            showOn: true,
            width: '550px',
            url: window.portal_url + "/getClients?_authenticator=" + $('input[name="_authenticator"]').val(),
            select: function( event, ui ) {
                $(this).val(ui.item.Title);
                $(this).change();
                $("input#ClientID").val(ui.item.ClientID)
                $("input#ClientID").change();
                return false;
            }
        });

        // the ContactName string field should have a lookup
        var getcontacts_url = window.location.href
            .split("/view")[0].split("/base_view")[0]
            .split("/edit")[0].split("/base_edit")[0] +  "/getContacts?_authenticator=" + $('input[name="_authenticator"]').val();
        $("input[id*='ContactName']").combogrid({
            colModel: [{'columnName':'Fullname','width':'100','label':_('Contact Name')}],
            showOn: true,
            width: '550px',
            url: getcontacts_url,
            select: function( event, ui ) {
                $(this).val(ui.item.Fullname);
                return false;
            }
        });

        // *Datepickers* on all Sample date fields
        var dateFormat = _("date_format_short_datepicker");
        if (dateFormat == 'date_format_short_datepicker'){
            dateFormat = 'yy-mm-dd';
        }
        $("input[id*=DateSampled]").live("click", function() {
            $(this).datepicker({
                showOn:"focus",
                showAnim:"",
                changeMonth:true,
                changeYear:true,
                dateFormat: dateFormat,
                yearRange: limitString
            })
            .click(function(){$(this).attr("value", "");})
            .focus();
        });

    }

}
