# -*- coding: utf-8 -*-

from odoo import models, api, fields, SUPERUSER_ID
from lxml import etree
from odoo.exceptions import AccessError, UserError
import json
import logging
_logger = logging.getLogger(__name__)


class ModelStateGroupPermission(models.Model):

    _name = "model.state.group.permission"
    group_id = fields.Many2one("res.groups", ondelete='cascade', required=True)
    model_name = fields.Char(string="Model Name", required=True, index=True)
    state_value = fields.Char(string="Model State Value", required=True)
    is_active = fields.Boolean(string="Is Active", default=True)
    is_hide_edit_button = fields.Boolean(string="Hide Edit Button", default=True)
    readonly_fields_name = fields.Text(string="Readonly fields")


class BaseStateModel(models.AbstractModel):

    _name = 'base_state_model.mixin'

    @api.multi
    def write(self, values):
        if self._uid != SUPERUSER_ID:
            self._check_write_state(values)
        super(BaseStateModel, self).write(values)
        return True

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(BaseStateModel, self).fields_view_get(view_id, view_type, toolbar, submenu)
        if self._uid != SUPERUSER_ID:
            return self._set_state_value_match_to_readonly(res, view_type)
        else:
            return res

    def _check_write_state(self, values):
        if "state" not in self._fields:
            raise UserError("state field not in %s, please add it.", self._name)
        state_groups_info = self._get_current_user_model_state_group_permission()
        if not state_groups_info:
            return True
        readonly_fields = []
        for model_state_group in state_groups_info:
            current_group_readonly_fields = model_state_group.readonly_fields_name.split(",")
            for field in current_group_readonly_fields:
                if field in values and field not in readonly_fields:
                    readonly_fields.append(field)
        if len(readonly_fields) > 0:
            raise AccessError("you have no access right to readonly fields:%s", ",".join(readonly_fields))
        return True

    def _get_current_user_model_state_group_permission(self):
        current_user_gids = self.env.user.groups_id.mapped("id")
        domain = [('model_name', '=', self._name), ("group_id", "in", current_user_gids), ("is_active", "=", True)]
        state_groups_info = self.env["model.state.group.permission"].sudo().search(domain)
        return state_groups_info

    def _set_state_value_match_to_readonly(self, res, view_type):
        if view_type != "form":
            return res
        state_groups_info = self._get_current_user_model_state_group_permission()
        if not state_groups_info:
            return res

        readonly_fields = []
        fiedls_condition = {}
        fiedls_group = {}

        for model_state_group in state_groups_info:
            current_group_readonly_fields = model_state_group.readonly_fields_name.split(",")
            group_name = model_state_group.group_id.full_name

            for field in current_group_readonly_fields:
                if field not in readonly_fields:
                    readonly_fields.append(field)
                if field not in fiedls_condition:
                    fiedls_condition[field] = [("state", "=", model_state_group.state_value)]
                    fiedls_group[field] = [group_name]
                else:
                    current_condition = fiedls_condition[field]
                    current_condition.insert(0, "|")
                    current_condition.append(("state", "=", model_state_group.state_value))

                    current_group = fiedls_group[field]
                    if group_name not in current_group:
                        current_group.append(group_name)

        doc = etree.XML(res["arch"])
        for field_name in readonly_fields:
            for node in doc.xpath("//field[@name='%s']" % field_name):
                domain = fiedls_condition[field_name]
                condition = {"readonly": domain}
                node.set("modifiers", json.dumps(condition))

                field_group = fiedls_group[field_name]
                result_group = ",".join(field_group)
                node.set("groups", result_group)

        res["arch"] = etree.tostring(doc)
        return res
