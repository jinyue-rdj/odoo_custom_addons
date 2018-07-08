from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class WechatCategoryController(http.Controller):

    @http.route('/api/v2/wechat_category', type='json', auth="user", sitemap=False)
    def wechat_category(self, **kw):
        result = {}
        result['is_success'] = True
        category_list = request.env['wechat.app.category'].sudo().get_categories()
        result['category_list'] = category_list
        if category_list and category_list[0]:
            app_list = request.env['wechat.app'].sudo().get_apps(category_list[0]["id"])
            result['current_app_list'] = app_list
            result['current_image_url'] = category_list[0]["thumb_url"]
            result['current_category_id'] = category_list[0]["id"]
            result['current_category_name'] = category_list[0]["name"]
            result['current_category_slogan'] = category_list[0]["slogan"]
        return result

    @http.route('/api/v2/wechat_app', type='json', auth="user", sitemap=False)
    def wechat_app_list(self, category_id, **kw):
        result = {}
        result['is_success'] = True
        app_list = request.env['wechat.app'].sudo().get_apps(category_id)
        category = request.env['wechat.app.category'].sudo().search([("id", "=", category_id)])
        result['current_app_list'] = app_list
        result['current_image_url'] = category.thumb_url
        result['current_category_id'] = category.id
        result['current_category_name'] = category.name
        result['current_category_slogan'] = category.slogan
        return result
