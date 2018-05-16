# -*- coding: utf-8 -*-
import werkzeug
import requests
import jwt
import datetime
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class WechatMiniProgramSession(models.Model):
    _name = 'wechat.mini.program.session'

    open_id = fields.Char(string="openid", required=True, index=True)
    union_id = fields.Char(string="unionid", required=True)
    session_key = fields.Char(string="session_key", required=True)
    user_id = fields.Many2one("res.users", required=False)

    @api.model
    def _get_openid(self, code):
        target_url = "https://api.weixin.qq.com/sns/jscode2session"

        ir_config_mini_program_appid = self.env['ir.config_parameter'].sudo().search([('key', '=', 'mini_program_appid')])
        appid = self.env['ir.config_parameter'].sudo().browse(int(ir_config_mini_program_appid))[0].value

        ir_config_mini_program_secret = self.env['ir.config_parameter'].sudo().search([('key', '=', 'mini_program_secret')])
        secret = self.env['ir.config_parameter'].sudo().browse(int(ir_config_mini_program_secret))[0].value

        request_paramters = {"appid": appid, "secret": secret, "js_code": code, "grant_type": "authorization_code"}
        paramters = werkzeug.url_encode(request_paramters)
        _logger.info("get openid parameters: %s", paramters)
        request_result = requests.get(target_url, params=paramters).json()

        if "errcode" in request_result:
            return False, request_result
        else:
            return True, request_result

    @api.model
    def _gen_3rd_session(self, openid, user_id):
        ir_config_pyjwt_secret_id = self.env['ir.config_parameter'].sudo().search([('key', '=', 'pyjwt_secret')])
        pyjwt_secret = self.env['ir.config_parameter'].sudo().browse(int(ir_config_pyjwt_secret_id))[0].value
        payload = {
            "iss": "cloudappservice.top",
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),
            "aud": "www.cloudappservice.top",
            "data": {
                "account_id": user_id
            }
        }
        token = jwt.encode(payload, pyjwt_secret, algorithm='HS256').decode('utf-8')
        return True, {"access_token": token, "account_id": user_id, "is_need_account": False, "message": "已生成token"}

    @api.model
    def verify_bearer_token(self, token):
        #  如果在生成token的时候使用了aud参数，那么校验的时候也需要添加此参数
        ir_config_pyjwt_secret_id = self.env['ir.config_parameter'].sudo().search([('key', '=', 'pyjwt_secret')])
        pyjwt_secret = self.env['ir.config_parameter'].sudo().browse(int(ir_config_pyjwt_secret_id))[0].value
        payload = jwt.decode(token, pyjwt_secret, audience='www.cloudappservice.top', algorithms=['HS256'])
        if payload:
            return True, payload
        return False, token

    @api.model
    def _openid2token(self, openid, session_key, union_id):
        db_openid = self.search([('open_id', '=', openid)])
        if db_openid:
            if db_openid[0].user_id:
                return self._gen_3rd_session(openid, db_openid[0].user_id.id)
            else:
                return False, {"is_get_openid": True, "is_need_account": True, "help_id": db_openid.id, "message": "openid数据已存在，但缺少用户信息"}
        else:
            new_db_openid = self.create({"open_id": openid, "union_id": union_id, "session_key": session_key})
            return False, {"is_get_openid": True, "is_need_account": True, "help_id": new_db_openid.id, "message": "openid数据已保存，但缺少用户信息"}

    @api.model
    def get_token(self, code):
        is_success, request_result = self._get_openid(code)
        if not is_success:
            return False, {"is_get_openid": False, "message": "获取失败"}
        else:
            openid = request_result["openid"]
            session_key = request_result["session_key"]
            union_id = ""
            if "unionid" in request_result:
                union_id = request_result["unionid"]
            return self._openid2token(openid, session_key, union_id)

