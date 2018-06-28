# -*- coding: utf-8 -*-

from odoo import models, api, fields
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
    edit_fields_name = fields.Text(string="Editable fields")


class BaseStateModel(models.AbstractModel):

    _name = 'base_state_model.mixin'

    @api.multi
    def write(self, values):
        self._check_write_state(values)
        super(BaseStateModel, self).write(values)
        return True

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(BaseStateModel, self).fields_view_get(view_id, view_type, toolbar, submenu)
        return self._set_state_value_match_to_readonly(res, view_type)

    def _check_write_state(self, values):
        if "state" not in self._fields:
            raise UserError("state field not in %s, please add it.", self._name)
        return True

    def _set_state_value_match_to_readonly1(self, res, view_type):
        editable_fields = ["remark", "project"]

        if view_type == "form":
            doc = etree.XML(res["arch"])
            for node in doc.xpath("/form/sheet/group/group/field"):
                field_name = node.get("name", False)
                _logger.info("name:%s", field_name)
                if field_name not in editable_fields:
                    #node.set("modifiers", '{"readonly": true}')
                    condition = {"readonly": ["!", ("state", "!=", "submit")]}
                    node.set("modifiers", json.dumps(condition))
            res["arch"] = etree.tostring(doc)
            return res
        else:
            return res

    def _set_state_value_match_to_readonly(self, res, view_type):
        if view_type != "form":
            return res
        _logger.info("BB")
        current_user_gids = self.env.user.groups_id.mapped("id")
        domain = [('model_name', '=', self._name)]
        state_groups_info = self.env["model.state.group.permission"].sudo().search(domain)
        doc = etree.XML(res["arch"])

        readonly_fields = []
        fiedls_condition = {}
        fiedls_group = {}
        for model_state_group in state_groups_info:
            _logger.info("CC")
            if model_state_group.group_id.id in current_user_gids:
                current_group_readonly_fields = model_state_group.edit_fields_name.split(",")
                readonly_fields = readonly_fields + current_group_readonly_fields

                group_name = model_state_group.group_id.full_name
                _logger.info("group_name:%s", group_name)
                for field in current_group_readonly_fields:
                    if field not in fiedls_condition:
                        fiedls_condition[field] = [("state", "=", model_state_group.state_value)]
                        fiedls_group[field] = [group_name]
                    else:
                        current_condition = fiedls_condition[field]
                        _logger.info("current_condition:%s", current_condition)
                        current_condition.insert(0, "|")
                        current_condition.append(("state", "=", model_state_group.state_value))

                        current_group = fiedls_group[field]
                        if group_name not in current_group:
                            current_group.append(group_name)
        _logger.info("fiedls_condition:%s", fiedls_condition)
        _logger.info("fiedls_group:%s", fiedls_group)
        for node in doc.xpath("/form/sheet/group/group/field"):
            field_name = node.get("name", False)
            if field_name in readonly_fields:
                domain = fiedls_condition[field_name]
                condition = {"readonly": domain}
                node.set("modifiers", json.dumps(condition))

                field_group = fiedls_group[field_name]
                result_group = ",".join(field_group)
                node.set("groups", result_group)

        res["arch"] = etree.tostring(doc)
        return res
