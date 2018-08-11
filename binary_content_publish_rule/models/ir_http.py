# -*- coding: utf-8 -*-
# Copyright (C) 2018 MAXSNS Corp (http://www.maxsns.com)
# @author Henry Zhou (zhouhenry@live.com)
# License OPL-1 - See https://www.odoo.com/documentation/user/11.0/legal/licenses/licenses.html

from odoo import api, models
from odoo import SUPERUSER_ID
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def binary_content(cls, xmlid=None, model='ir.attachment', id=None, field='datas',
                       unique=False, filename=None, filename_field='datas_fname', download=False,
                       mimetype=None, default_mimetype='application/octet-stream',
                       access_token=None, env=None):
        env = env or request.env

        obj = None
        if xmlid:
            obj = env.ref(xmlid, False)
        elif id and model in env:
            obj = env[model].browse(int(id))

        if obj and obj.exists() and model == "ir.attachment":
            # if obj don't use sudo() function, it has no right to access the res_model field
            parameter = 'binary.content.publish.rule.' + obj.sudo().res_model
            field_names = request.env['ir.config_parameter'].sudo().get_param(parameter, '')
            field_list = field_names.strip(',').split(',')
            if field_list and field in field_list:
                env = env(user=SUPERUSER_ID)
        return super(Http, cls).binary_content(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
            filename_field=filename_field, download=download, mimetype=mimetype,
            default_mimetype=default_mimetype, access_token=access_token, env=env)
