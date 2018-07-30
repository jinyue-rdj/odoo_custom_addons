# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from openerp.http import request

_logger = logging.getLogger(__name__)


class WechatAppCategory(models.Model):
    _name = "wechat.app.category"

    name = fields.Char(string="CategoryName")
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
            result["thumb_url"] = self.get_attachment_url(app_category.id)
            result["order"] = app_category.order
            result["id"] = app_category.id
            result["slogan"] = app_category.slogan
            app_category_list_result.append(result)
        return app_category_list_result

    def get_attachment_url(self, category_id):
        url = request.httprequest.environ.get('HTTP_HOST', '') + "/web/image/%s/300x300"
        attachment = self.env["ir.attachment"].search([("res_id", "=", category_id), ("res_model", "=", self._name)], limit=1)
        if attachment:
            return url % str(attachment.id)
        else:
            return url % "0"

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
        for new in self:
            new.image_count = attachment.search_count([
                '&', ('res_model', '=', self._name), ('res_id', '=', new.id)
            ])

    image_count = fields.Integer(compute='_compute_attached_images_count', string="Number of documents attached")

