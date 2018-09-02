# -*- coding: utf-8 -*-
import werkzeug
import json
from urllib.parse import urlparse
from urllib import request
import requests
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class WeChatAccount(models.Model):
    _name = 'wechat.mini.program.account'
    _description = "WeChat Account"

    wechat_app_id = fields.Char(string="WeChat App ID", required=True)
    wechat_open_id = fields.Char(string="WeChat Open ID", required=True, index=True)
    user_id = fields.Many2one("res.users", string="User", required=True)

    _sql_constraints = [
        ('wechat_open_id_uniq', 'unique(wechat_app_id, wechat_open_id)',
         'The wechat_open_id must be unique per wechat_app_id!'),
    ]

    def check_third_part_login(self, login, pwd):
        params = werkzeug.url_encode({'name': login, 'pwd': pwd})
        web_target_url = 'https://wuzffalu.cn.flextronics.com/flexpsappapi/api/UserLoginAndRegister/Login'
        result = requests.get(web_target_url, params=params).json()
        user_id = False
        if result["IsSuccess"]:
            user_id = self._get_or_create_user(login, result["LoginName"])
        return user_id

    def _get_or_create_user(self, login, name):
        res_company = self.env['res.company'].search([])
        values = {"login": login, "name": name, "company_id": res_company[0].id, "active": True}
        sudo_user = self.env['res.users'].sudo()
        odoo_users = sudo_user.search([("login", "=", login)])
        if odoo_users:
            user_id = odoo_users[0].id
        else:
            user_id = odoo_users.create(values).id
        return user_id

    def update_or_create_wechat_account_user(self, openid, appid, uid):
        account = self.search([('wechat_open_id', '=', openid), ('wechat_app_id', '=', appid)])
        if account:
            if account.user_id.id != uid:
                account.write({'user_id': uid})
        else:
            self.create({
                'wechat_open_id': openid,
                'user_id': uid,
                'wechat_app_id': appid,
            })
