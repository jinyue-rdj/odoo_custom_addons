# -*- coding: utf-8 -*-

from odoo import models, api, fields
import logging
_logger = logging.getLogger(__name__)


class ModelStateGroupPermission(models.Model):

    _name = "model.state.group.permission"
    group_id = fields.Many2one("res.groups", ondelete='cascade', required=True)
    model_name = fields.Char(string="Model Name", required=True, index=True)
    state = fields.Char(string="Model State Value", required=True)
    perm_read = fields.Boolean(string="Can Read", default=True)
    perm_write = fields.Boolean(string="Can Write", default=False)
    perm_create = fields.Boolean(string="Can Create", default=False)
    perm_unlink = fields.Boolean(string="Can Delete", default=False)
    remark = fields.Text()

