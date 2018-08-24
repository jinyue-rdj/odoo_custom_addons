from odoo import http, tools
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class WechatSplashController(http.Controller):

    @http.route('/api/v2/wechat_splash', type='json', auth="none", sitemap=False)
    def wechat_splash(self, **kw):
        result = {}
        result['is_success'] = True
        try:
            splash_list = request.env['wechat.app.splash'].sudo().get_splash()
            result['splash_list'] = splash_list
        except Exception as e:
            result['is_success'] = False
            result['info'] = tools.ustr(e)
        return result

