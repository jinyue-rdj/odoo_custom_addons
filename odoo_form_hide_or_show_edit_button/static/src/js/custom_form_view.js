odoo.define('odoo_form_hide_or_show_edit_button.custom_form_view', function (require) {
"use strict";

var core = require('web.core');
var FormController = require('web.FormController');
var ajax = require('web.ajax');

var _t = core._t;
var QWeb = core.qweb;

FormController.include
({
	renderButtons: function(node)
	{
	    this._super.apply(this, node);
	    var that = this;
        ajax.jsonRpc('/web/getModeState', 'call', {'model_name': that.modelName }).then(function (data)
        {
            console.log(data)
            if(data.is_success && data.has_state)
            {
                 var result = data.data;
                 var record = that.model.get(that.handle, {raw: true});
                 for(var i = 0; i< result.length; i++)
                 {
                     if(result[i].state_value == record.data.state)
                     {
                          that.$buttons.find('.o_form_button_edit').attr('disabled', result[i].is_hide_edit_button);
                          break;
                     }
                 }
             }
        });
	}
});

});