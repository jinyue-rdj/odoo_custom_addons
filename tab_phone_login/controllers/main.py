# -*- encoding: utf-8 -*-

import odoo
from odoo import http
from odoo.addons.web.controllers.main import ensure_db
import odoo.addons.web.controllers.main as main
from odoo.http import request

from odoo import registry as registry_get
from odoo import api, http, SUPERUSER_ID, _
import random
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class LoginHome(main.Home):

    @http.route('/web/phonelogin', type='http', auth="none", sitemap=False)
    def web_phone_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None
        if request.httprequest.method == 'POST':
            with registry_get(request.params['phone_db']).cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                expiration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                users = env['res.users'].sudo().search([('partner_id.mobile', '=', request.params['phone']), ('verify_code', '=', request.params['checkCode']), ('expiration_date', '>', expiration_date)])
                if users:
                    # request.httprequest.environ['phone'] = request.params['phone']
                    # request.httprequest.environ['checkCode'] = request.params['checkCode']
                    request.session.authenticate(request.params['phone_db'], users[0].login, users[0].password_crypt)
                    request.params['login_success'] = True
                    if not redirect:
                        redirect = '/web'
                    return http.redirect_with_hash(self._login_redirect(users[0].id, redirect=redirect))
                else:
                    values['phone_error'] = _("check code is not correct!")
                    return request.render('web.login', values)

    @http.route('/web/getCheckCode', type='json', auth="none")
    def get_verify_code(self, phone=None, **kw):
        _logger.info('phone is %s', phone)
        result = {}
        with registry_get(request.session.db).cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                users = env['res.users'].sudo().search([('partner_id.mobile', '=', phone)])
                if users:
                    expiration_date = datetime.now() + timedelta(minutes=5)
                    users[0].write({'verify_code': self.generate_verify_code(), 'expiration_date': expiration_date})
                    cr.commit()
                    result['is_success'] = True
                    result['phone_message'] = 'we send it to you'
                else:
                    result['is_success'] = False
                    result['phone_message'] = 'your phone no exist'
        return result

    def generate_verify_code(self):
        code_list = []
        for i in range(10):
            code_list.append(str(i))
        my_slice = random.sample(code_list, 6)
        verification_code = ''.join(my_slice)
        return verification_code

