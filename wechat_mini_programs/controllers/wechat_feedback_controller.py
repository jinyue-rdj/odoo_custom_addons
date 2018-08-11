from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class WechatFeedbackController(http.Controller):

    @http.route('/api/v2/wechat_feedback', type='json', auth="user", sitemap=False)
    def wechat_save_feedback(self, content, contact, **kw):
        user_id = request.env.user.id
        result = request.env['wechat.feedback'].sudo().save_data(content, contact, user_id)
        return result

