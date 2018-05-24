# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class NewsCategory(models.Model):
    _name = "news.category"

    name = fields.Char()

