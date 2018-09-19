from odoo import http, tools
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class WechatProjectViewController(http.Controller):

    @http.route('/api/v2/wechat_project_news', type='json', auth="user")
    def wechat_get_project_news(self, page_index, page_size, **kw):
        result = {'is_success': True}
        try:
            data = request.env['invest.news'].sudo().get_news_list_page(page_index, page_size)
            result['data'] = data
        except Exception as e:
            result = {'is_success': False, 'info': tools.ustr(e)}
        return result

    @http.route('/api/v2/wechat_project_news_detail', type='json', auth="user", sitemap=False)
    def get_news_detail(self, news_id, **kw):
        result = {}
        result['is_success'] = True
        try:
            detail = request.env['invest.news'].sudo().get_news_detail(news_id)
            result['news_detail'] = detail
        except Exception as e:
            result = {'is_success': False, 'info': tools.ustr(e)}
        return result
