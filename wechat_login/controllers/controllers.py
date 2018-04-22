# coding=utf-8

from odoo.http import request
from odoo.addons.auth_oauth.controllers.main import OAuthLogin

import werkzeug
import json
import logging
from collections import OrderedDict
_logger = logging.getLogger(__name__)


class WechatLogin(OAuthLogin):

    def _get_wechat_auth_link(self):
        provider_id = request.env.ref("wechat_login.provider_wechat").id
        provider = request.env['auth.oauth.provider'].sudo().search([('id', '=', provider_id)])
        return_url = request.httprequest.url_root + 'auth_oauth/signin'
        return_url = 'https://www.cloudappservice.top/' + 'auth_oauth/signin'
        state = self.get_state(provider)
        '''use OrderedDict is very important,cause the wechat will checked them by order'''
        params = OrderedDict()
        params['appid'] = provider['client_id']
        params['redirect_uri'] = return_url
        params['response_type'] = 'code'
        params['scope'] = provider['scope']
        params['state'] = json.dumps(state)
        parameter_url = (provider['auth_endpoint'], werkzeug.url_encode(params), '#wechat_redirect')
        return provider_id, "%s?%s%s" % parameter_url

    def _deal_providers(self, providers):
        wechat_provider_id, wechat_url = self._get_wechat_auth_link()
        for provider in providers:
            if provider['id'] == wechat_provider_id:
                provider['auth_link'] = wechat_url

    def list_providers(self):
        providers = super(WechatLogin, self).list_providers()
        self._deal_providers(providers)
        return providers
