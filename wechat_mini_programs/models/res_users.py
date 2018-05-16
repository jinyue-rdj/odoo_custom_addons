# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ResUser(models.Model):
    _inherit = 'res.users'

    open_ids = fields.One2many("wechat.mini.program.session", "open_id")

    @api.model
    def create_wechat_mini_user(self, name, mini_program_id):
        values = {"login": name, "name": name, "password": "", 'company_id': 1}
        db_openid = self.env['wechat.mini.program.session'].sudo().search([('id', '=', mini_program_id)])
        _logger.error("begin")
        if db_openid and db_openid[0].user_id:
            _logger.error("if")
            return db_openid[0].user_id.id
        else:
            _logger.error("else")
            user_id = self.sudo().create(values).id
            _logger.error("ok")
            db_openid.write({"user_id": user_id})
            return user_id


