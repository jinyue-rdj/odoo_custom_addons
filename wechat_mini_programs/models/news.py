# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class News(models.Model):
    _name = "news"

    title = fields.Char()
    content = fields.Html()
    is_banner = fields.Boolean()
    is_publish = fields.Boolean()
    category_id = fields.Many2one("news.category")


    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        domain = ['&', ('res_model', '=', 'news'), ('res_id', 'in', self.ids)]

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
                '&', ('res_model', '=', 'news'), ('res_id', '=', new.id)
            ])

    image_count = fields.Integer(compute='_compute_attached_images_count', string="Number of documents attached")
