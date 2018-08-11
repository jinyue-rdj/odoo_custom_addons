import json
from odoo import http
from odoo.http import request
import base64
import logging
_logger = logging.getLogger(__name__)


class AppUploadController(http.Controller):

    @http.route('/api/base64/upload_attachment', type='json', auth="user")
    def wechat_upload_attachment_base64(self, model, id, ufile, **kw):
        _logger.info("upload file begin")
        attachment_model = request.env['ir.attachment']
        result = []
        try:
            attachment = attachment_model.sudo().create({
                'name': 'wechat_image',
                'datas': ufile,
                'datas_fname': 'wechat_image',
                'res_model': model,
                'res_id': int(id)
            })
            result.append({'file_name': ufile, 'is_success': True})
        except Exception:
            result.append({'file_name': ufile, 'is_success': False})
            _logger.exception("Fail to upload attachment")
        return result

    @http.route('/api/binary/upload_attachment', type='http', auth="user", csrf=False)
    def wechat_upload_attachement(self, model, id, **kw):
        files  = request.httprequest.files.getlist('ufile')
        attachement_model = request.env['ir.attachment']
        result = []
        for f in files:
            file_name = f.filename
            _logger.info("file ia %s", file_name)
            try:
                attachement_model.sudo().create({
                    'name': file_name,
                    'datas': base64.encodestring(f.read()),
                    'datas_fname': file_name,
                    'res_model': model,
                    'res_id': int(id)
                })
                result.append({'file_name': file_name, 'is_success': True})
            except Exception:
                result.append({'file_name': file_name, 'is_success': False})
        return json.dumps(result)
