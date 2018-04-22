# -*- coding: utf-8 -*-
import werkzeug
import json
from urllib.parse import urlparse
from urllib import request
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):

    _inherit = 'res.users'

    def _auth_oauth_wechat_rpc(self, client_id, validation_endpoint, data_endpoint, code, secret):
        params = werkzeug.url_encode({'code': code, 'appid': client_id, 'secret': secret, 'grant_type': 'authorization_code'})
        url = validation_endpoint + '?' + params
        _logger.info('Request %s to get access_token'%url)
        f = request.urlopen(url)
        response = f.read()
        validation = json.loads(response)
        if 'access_token' in validation:
            params = werkzeug.url_encode({'access_token': validation['access_token'], 'openid': validation['openid']})
            url = data_endpoint + '?' + params
            logger.info('Request %s to get userinfo'%url)
            f = request.urlopen(url)
            response = f.read()
            validation = json.loads(response)
            if 'unionid' in validation:
                validation['user_id'] = validation['unionid']
            if 'nickname' in validation:
                validation['name'] = validation['nickname']
        return validation

    @api.model
    def _auth_oauth_validate(self, provider, access_token):
        """ return the validation data corresponding to the access token """
        wechat_provider_id = request.env.ref("wechat_login.provider_wechat").id
        oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        if oauth_provider.id == wechat_provider_id:
            ir_config_wechat_id = request.env['ir.config_parameter'].sudo().search([('key', '=', 'wechat_login.secret')])
            wechat_secret = request.env['ir.config_parameter'].sudo().browse(int(ir_config_wechat_id))[0].value
            validation = self._auth_oauth_wechat_rpc(oauth_provider.client_id, oauth_provider.validation_endpoint, oauth_provider.data_endpoint, access_token ,wechat_secret)
            return validation
        else:
            return super(ResUsers, self)._auth_oauth_validate(provider, access_token)

    @api.model
    def auth_oauth(self, provider, params):
        code = params.get('code', None)
        if code:
            params['access_token'] = code
        return super(ResUsers, self).auth_oauth(provider, params)
