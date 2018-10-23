# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from openerp.http import request
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

    def get_news_detail(self, news_id):
        detail = self.search([("id", "=", news_id)])
        return detail

    def get_list(self):
        result = {}
        result['is_success'] = True
        url = self.get_image_url()
        sql = """SELECT A.id, A.title, A.is_banner, A.category_id, to_char(A.create_date,'yyyy-mm-dd') create_date,B.Name,
                 '%s' || cast(C.Id as Text) url
                              FROM news A left join news_category B 
                              on A.category_id = B.id 
                              left join ir_attachment C 
                              on A.id  =  C.res_id 
                              where A.is_banner  = %s 
                              and  A.is_publish = true 
                              and C.res_model='%s' 
                              order by A.create_date desc
                              limit %d
              """
        banner_sql = sql % (url, "true", "news", 5)
        news_sql = sql % (url, "false", "news", 10)
        self.env.cr.execute(banner_sql)
        result['banner_list'] = self.env.cr.dictfetchall()
        self.env.cr.execute(news_sql)
        result['news_list'] = self.env.cr.dictfetchall()
        return result

    def get_list_page(self, page_index, page_size):
        result = {}
        result['is_success'] = True
        offset = (int(page_index) - 1) * int(page_size)
        url = self.get_image_url()
        sql = """SELECT A.id, A.title, A.is_banner, A.category_id, to_char(A.create_date,'yyyy-mm-dd') create_date,B.Name
                 ,'%s' || cast(C.Id as Text) url
                  FROM news A left join news_category B 
                  on A.category_id = B.id 
                  left join ir_attachment C 
                  on A.id  =  C.res_id 
                  where A.is_publish = true 
                  and C.res_model='%s' 
                  order by A.create_date desc
                  limit %s offset %d
              """
        news_sql = sql % (url, "news", page_size, offset)
        self.env.cr.execute(news_sql)
        result['news_list'] = self.env.cr.dictfetchall()
        return result

    def get_group_list(self):
        result = {}
        first_sql = """SELECT a.*
                              FROM ir_model_access a
                              JOIN ir_model m ON (m.id = a.model_id)
                              JOIN res_groups_users_rel gu ON (gu.gid = a.group_id)
                              WHERE m.model = '%s'
                              AND gu.uid = %d
                              AND a.active IS TRUE
                      """
        second_sql = """  SELECT a.*
                          FROM ir_model_access a
                          JOIN ir_model m ON (m.id = a.model_id)
                          WHERE a.group_id IS NULL
                          AND m.model = '%s'
                          AND a.active IS TRUE
                     """
        news_sql = first_sql % (self._name, self._uid)
        special_sql = second_sql % self._name
        self.env.cr.execute(news_sql)
        result['first_list'] = self.env.cr.dictfetchall()
        self.env.cr.execute(special_sql)
        result['second_list'] = self.env.cr.dictfetchall()
        return result

    def get_image_url(self):
        return request.httprequest.url_root + "web/image/"
