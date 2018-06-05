odoo.define('tab_phone_login.tab_phoneLogin',function(require)
{
    'use strict';
    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    var wait = 60;
    var isEnabledClicked = true;
    function down_time(target)
    {
          if(wait  ==  0)
          {
                isEnabledClicked = true;
                target.removeClass('disabled');
                target.html('Resend Code');

                wait = 60;
          }
          else
          {
                isEnabledClicked = false;
                target.addClass('disabled');
                target.html('Resend('+wait+')');
                wait--;
                console.log(wait);
                setTimeout(function(){
                    down_time(target);
                },1000);
          }
    }

    $('#CheckCodeId').on('click', function (ev)
    {
      if(isEnabledClicked)
      {
            ajax.jsonRpc('/web/getCheckCode', 'call', {'phone': $('#phone').val()}).then(function (data)
            {
                    if(data.is_success)
                    {
                       down_time($('#CheckCodeId'));
                    }
                    else
                    {

                    }
                    $('#CheckCodeId').tooltip({'title':data.phone_message});
            });
       }
    });
})