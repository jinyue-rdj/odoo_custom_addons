# -*- encoding: utf-8 -*-
##############################################################################
#
#    Samples module for Odoo Web Login Screen
#    Copyright (C) 2017- XUBI.ME (http://www.xubi.me)
#    @author binhnguyenxuan (https://www.linkedin.com/in/binhnguyenxuan)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    
#
##############################################################################
import werkzeug
import werkzeug.utils
import ast
from odoo.addons.web.controllers.main import Home, ensure_db
import pytz
import datetime
import logging

import odoo
import odoo.modules.registry
from odoo import http
from odoo.http import request
_logger = logging.getLogger(__name__)


# ----------------------------------------------------------
# Odoo Web web Controllers
# ----------------------------------------------------------

class LoginHome(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        param_obj = request.env['ir.config_parameter'].sudo()
        request.params['disable_footer'] = ast.literal_eval(param_obj.get_param('login_form_disable_footer')) or False
        request.params['disable_database_manager'] = ast.literal_eval(
            param_obj.get_param('login_form_disable_database_manager')) or False

        change_background = ast.literal_eval(param_obj.get_param('login_form_change_background_by_hour')) or False
        if change_background:
            config_login_timezone = param_obj.get_param('login_form_change_background_timezone')
            tz = config_login_timezone and pytz.timezone(config_login_timezone) or pytz.utc
            current_hour = datetime.datetime.now(tz=tz).hour or 10

            if (current_hour >= 0 and current_hour < 3) or (current_hour >= 18 and current_hour < 24):  # Night
                request.params['background_src'] = param_obj.get_param('login_form_background_night') or ''
            elif current_hour >= 3 and current_hour < 7:  # Dawn
                request.params['background_src'] = param_obj.get_param('login_form_background_dawn') or ''
            elif current_hour >= 7 and current_hour < 16:  # Day
                request.params['background_src'] = param_obj.get_param('login_form_background_day') or ''
            else:  # Dusk
                request.params['background_src'] = param_obj.get_param('login_form_background_dusk') or ''
        else:
            request.params['background_src'] = param_obj.get_param('login_form_background_default') or ''
        return super(LoginHome, self).web_login(redirect, **kw)

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        ensure_db()
        if not request.session.uid:
            return werkzeug.utils.redirect('/web/login', 303)
        if kw.get('redirect'):
            return werkzeug.utils.redirect(kw.get('redirect'), 303)

        request.uid = request.session.uid
        try:
            context = request.env['ir.http'].webclient_rendering_context()
            '''
                 invoke my private method to check
            '''
            context = self._set_menu_left_down_parameters(context)
            response = request.render('web.webclient_bootstrap', qcontext=context)
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        except AccessError:
            return werkzeug.utils.redirect('/web/login?error=access')

    def _set_menu_left_down_parameters(self, context):
        param_obj = request.env['ir.config_parameter'].sudo()
        logo_value = ast.literal_eval(param_obj.get_param('disable_left_down_menu_logo_footer')) or False
        if not logo_value:
            context['left_down_menu_logo_power'] = param_obj.get_param('left_down_menu_logo_power') or ''
            context['left_down_menu_logo_url'] = param_obj.get_param('left_down_menu_logo_url') or ''
            context['left_down_menu_logo_name'] = param_obj.get_param('left_down_menu_logo_name') or 'A'
        context['disable_left_down_menu_logo_footer'] = logo_value
        return context
