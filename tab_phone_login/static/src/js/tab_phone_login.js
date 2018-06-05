/*odoo.define('tab_phoneLogin',function(require)
{

})*/
(function()
{
      if (typeof window === "undefined")
      {
         return;
      }
      window.Authy = {};
      window.Authy.UI = function()
      {
          self = this;
          BindCheckCodeEvent = function()
          {
              checkCode = document.getElementById("checkCode");
              checkCode.value = "Hello world";
              $("#CheckCodeId").click(function()
               {
                    console.log('I will send check code');
                    $.ajax({
	                            'async': true,
	                            'url': '/web/getCheckCode',
	                            'dataType': "text",
	                            'success': function (data)
                                {
                                    console.log(data);
                                    $("#checkCode").val(data);
                                }
	                        })
               });
          },
          this.init = function()
          {
                BindCheckCodeEvent();
          }
      }

      Authy.UI.instance = function()
      {
            if (!this.ui)
            {
                this.ui = new Authy.UI();
                this.ui.init();
            }
            return this.ui;
      };

      window.onload = function()
      {
            return Authy.UI.instance();
      };

}).call(this);