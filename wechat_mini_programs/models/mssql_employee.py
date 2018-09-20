# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api
from odoo import tools

_logger = logging.getLogger(__name__)


class MsslEmployee(models.Model):
    _name = "mssql.employee"
    _auto = False

    name = fields.Char(readonly=True)
    employee_no = fields.Char(readonly=True)

    @api.model_cr
    def init(self):
        tools.sql.drop_view_if_exists(self.env.cr, self._table)
        query = """
        create view %s as
        SELECT A.id,  A.login as name, B.street as employee_no
        FROM res_users A
        left join res_partner B
        on A.Id = B.user_id
        """ % self._table
        self.env.cr.execute(query)

