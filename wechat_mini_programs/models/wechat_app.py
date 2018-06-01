# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class WechatApp(models.Model):
    _name = "wechat.app"

    name = fields.Char(string="AppName")
    thumb_url = fields.Char(string="Image Url")
    short_code = fields.Char(string="App Short Code")
    is_enabled = fields.Boolean()
    app_category_id = fields.Many2one("wechat.app.category")
    order = fields.Integer(string="Order")
    wechat_page_url = fields.Char(string="Wechat Url")

    def get_apps(self, category_id):
        app_list_result = []
        app_list = self.search([("app_category_id.id", "=", category_id), ("is_enabled", "=", True)], order="order")
        for app in app_list:
            result = {}
            result["name"] = app.name
            result["thumb_url"] = app.thumb_url
            result["order"] = app.order
            result["wechat_page_url"] = app.wechat_page_url
            app_list_result.append(result)
        return app_list_result


