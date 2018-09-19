# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class InvestNews(models.Model):
    _name = "invest.news"

    title = fields.Char(string="NewsTitle")
    content = fields.Html(string="NewsContent")
    is_publish = fields.Boolean(string="Is Publish")

    def get_news_detail(self, news_id):
        detail = self.search([("id", "=", news_id)])
        return detail

    def get_news_list_page(self, page_index, page_size):
        result = []
        offset = (int(page_index) - 1) * int(page_size)
        domain = [("is_publish", "=", True)]
        list = self.search(domain, offset=offset, limit=page_size, order='create_date desc')
        for l in list:
            item = {}
            item["title"] = l.title
            item["content"] = l.content
            item["create_date"] = l.create_date
            result.append(item)
        return result
