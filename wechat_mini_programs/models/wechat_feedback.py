# -*- coding: utf-8 -*-

import datetime
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class NewsCategory(models.Model):
    _name = "wechat.feedback"

    content = fields.Text(string="Content", required=True)
    contact = fields.Char()
    user_id = fields.Many2one("res.users", string="User", required=True)
    feedback_date = fields.Datetime()
    is_processed = fields.Boolean(default=False)
    processed_content = fields.Text()

    def save_data(self, content, contact, user_id):
        result = {"is_success": True, "model": self._name}
        try:
            feedback = self.create({
                'content': content,
                'contact': contact,
                'user_id': user_id,
                'feedback_date': datetime.datetime.now(),
                'is_processed': False
            })
            result["res_id"] = feedback.id
        except Exception:
            result["is_success"] = False
        return result

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
        for feedback in self:
            feedback.image_count = attachment.search_count([
                '&', ('res_model', '=', self._name), ('res_id', '=', feedback.id)
            ])

    image_count = fields.Integer(compute='_compute_attached_images_count', string="Number of documents attached")

