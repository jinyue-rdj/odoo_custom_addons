# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class WechatAppCategory(models.Model):
    _name = "wechat.app.category"

    name = fields.Char(string="CategoryName")
    thumb_url = fields.Char(string="Image Url")
    short_code = fields.Char(string="Short Code")
    is_enabled = fields.Boolean()
    order = fields.Integer(string="Order")
    slogan = fields.Char(string="Slogan")

    def get_categories(self):
        app_category_list_result = []
        app_category_list = self.search([("is_enabled", "=", True)], order="order")
        for app_category in app_category_list:
            result = {}
            result["name"] = app_category.name
            result["thumb_url"] = app_category.thumb_url
            result["order"] = app_category.order
            result["id"] = app_category.id
            result["slogan"] = app_category.slogan
            app_category_list_result.append(result)
        return app_category_list_result
