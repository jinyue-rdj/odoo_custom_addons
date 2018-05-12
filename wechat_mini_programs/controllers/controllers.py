# -*- encoding: utf-8 -*-

import werkzeug
import requests
import json
import odoo.addons.web.controllers.main as main
from odoo import registry as registry_get
from odoo import api, http, SUPERUSER_ID, _
import logging

_logger = logging.getLogger(__name__)


class WechatMiniProgram(main.Home):

    @http.route('/web/transfer', type='http', auth="none", sitemap=False)
    def transfer_request(self, target_url, request_paramters):
        result = {}
        result['is_success'] = True

        target_url = "https://wuzffalu.cn.flextronics.com/flexpsappapi/api/" + target_url
        try:
            request_paramters = json.loads(request_paramters)
            request_paramters = werkzeug.url_encode(request_paramters)
            request_result = requests.get(target_url, params=request_paramters).json()
            result['data'] = request_result
        except:
            result['is_success'] = False
            pass

        result = json.dumps(result)
        return result

    @http.route('/web/gettoken', type='http', auth="none", sitemap=False)
    def get_wechat_openid(self, code, db_name):
        result = {}
        result['is_success'] = True

        try:
            with registry_get(db_name).cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                is_success, token = env['wechat.mini.program.session'].get_token(code)
                _logger.info("token is %s", token)
                result['token'] = token
                result['is_get_token'] = is_success
                #success2, token2 = env['wechat.mini.program.session'].verify_bearer_token(token['access_token'])
                #_logger.info("token2 is %s", token2)
                cr.commit()
        except:
            result['is_success'] = False
            pass

        result = json.dumps(result)
        return result

    @http.route('/web/create_user', type='http', auth="none", sitemap=False)
    def create_user(self, login_name, help_id, db_name):
        result = {}
        result['is_success'] = True
        _logger.info("user_id begin ")
        try:
            with registry_get(db_name).cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                user_id = env['res.users'].create_wechat_mini_user(login_name, help_id)
                _logger.info("user_id is %d", user_id)
                result['user_id'] = user_id
                cr.commit()
        except:
            result['is_success'] = False
            pass

        result = json.dumps(result)
        return result
