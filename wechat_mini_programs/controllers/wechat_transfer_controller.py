import werkzeug
import json
import requests
from odoo import http
import logging
_logger = logging.getLogger(__name__)


class WechatTransferController(http.Controller):

    @http.route('/api/v2/wechat_transfer', type='json', auth="user", sitemap=False)
    def transfer_web_url(self, target_url, request_paramters, **kw):
        result = {}
        result['is_success'] = True
        web_target_url = '%s%s' % ('https://wuzffalu.cn.flextronics.com/flexpsappapi/api/', target_url)
        try:
            request_paramters = json.loads(request_paramters)
            request_paramters = werkzeug.url_encode(request_paramters)
            request_result = requests.get(web_target_url, params=request_paramters).json()
            result['data'] = request_result
        except:
            result['is_success'] = False
            pass
        return result
