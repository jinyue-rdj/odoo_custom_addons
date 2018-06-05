# -*- coding: utf-8 -*-

from odoo import models, api, fields
from odoo.exceptions import AccessDenied
import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    verify_code = fields.Char(string="Verify Code")
    expiration_date = fields.Datetime('CheckCode Expiration Date')

    @api.model
    def check_credentials(self, password):

        try:
            super(ResUsers, self).check_credentials(password)
        except AccessDenied:
            user = self.sudo().search([('id', '=', self._uid), ('password_crypt', '=', password)])
            if not user:
                _logger.info('failed to login,id is %d,password is %s', self._uid, password)
                raise AccessDenied()
