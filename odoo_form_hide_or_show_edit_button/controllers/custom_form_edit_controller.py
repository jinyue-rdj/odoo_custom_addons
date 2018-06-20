# -*- encoding: utf-8 -*-

from odoo import api, http, SUPERUSER_ID, _
import logging

_logger = logging.getLogger(__name__)


class CustomFormEditController(http.Controller):

    @http.route('/web/getModeState', type='json', auth="user")
    def get_verify_code(self, model_name=None, **kw):
        _logger.info(model_name)
        result = {}
        result['is_success'] = True
        result['has_state'] = True
        result['model'] = model_name
        result['data'] = [{"state": "confirm", "is_write": False}, {"state": "completed", "is_write": False}]
        return result


