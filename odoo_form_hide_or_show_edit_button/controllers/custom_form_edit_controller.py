# -*- encoding: utf-8 -*-

from odoo import api, http, SUPERUSER_ID, _
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class CustomFormEditController(http.Controller):

    @http.route('/web/getModeState', type='json', auth="user")
    def get_verify_code(self, model_name=None, **kw):
        _logger.info(model_name)
        result = {}
        result['is_success'] = True
        result['has_state'] = False
        result['model'] = model_name
        try:
            groups_id = request.env.user.groups_id
            model_permission_list = request.env['model.state.group.permission'].sudo().search([
                ("model_name", "=", model_name),
                ("group_id", "in", groups_id.ids)
            ])
        except Exception as e:
            result['is_success'] = False

        if model_permission_list:
            result['has_state'] = True
            result['data'] = []
            for item in model_permission_list:
                result['data'].append({"state": item.state, "is_write": item.perm_write})
        return result


