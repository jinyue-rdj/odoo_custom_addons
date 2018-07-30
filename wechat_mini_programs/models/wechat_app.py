# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from openerp.http import request
_logger = logging.getLogger(__name__)


class WechatApp(models.Model):
    _name = "wechat.app"

    name = fields.Char(string="AppName")
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
            result["thumb_url"] = self.get_attachment_url(app.id)
            result["order"] = app.order
            result["wechat_page_url"] = app.wechat_page_url
            app_list_result.append(result)
        return app_list_result

    def get_attachment_url(self, app_id):
        url = request.httprequest.environ.get('HTTP_HOST', '') + "/web/image/%s/300x300"
        attachment = self.env["ir.attachment"].search([("res_id", "=", app_id), ("res_model", "=", self._name)], limit=1)
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



