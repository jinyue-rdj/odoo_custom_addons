# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from openerp.http import request

_logger = logging.getLogger(__name__)


class WechatAppSplash(models.Model):
    _name = "wechat.app.splash"

    name = fields.Char(string="AppName")
    app_author = fields.Char(string="Author")
    is_enabled = fields.Boolean()
    copy_right = fields.Char(string="CopyRight")

    def get_splash(self):
        app_splash_list_result = []
        app_splash_list = self.search([("is_enabled", "=", True)], limit=1)
        for app_splash in app_splash_list:
            result = {}
            result["app_name"] = app_splash.name
            result["app_splash_url"] = self.get_attachment_url(app_splash.id)
            result["app_author"] = app_splash.app_author
            result["app_copy_right"] = app_splash.copy_right
            app_splash_list_result.append(result)
        return app_splash_list_result

    def get_attachment_url(self, app_splash_id):
        url = request.url_root + "web/image/%s"
        attachment = self.env["ir.attachment"].search([("res_id", "=", app_splash_id), ("res_model", "=", self._name)], limit=1)
        if attachment:
            return url % str(attachment.id)
        else:
            return ""

    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        domain = ['&', ('res_model', '=', self._name), ('res_id', 'in', self.ids)]

        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Documents are attached to the tasks and issues of your news.</p><p>
                        Send messages or log internal notes with attachments to link
                        documents to your views.
                    </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    def _compute_attached_images_count(self):
        attachment = self.env['ir.attachment']
        for model in self:
            model.image_count = attachment.search_count([
                '&', ('res_model', '=', self._name), ('res_id', '=', model.id)
            ])

    image_count = fields.Integer(compute='_compute_attached_images_count', string="Number of documents attached")

