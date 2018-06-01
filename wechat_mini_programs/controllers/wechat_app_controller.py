import json
from odoo import http, api
from odoo.modules.registry import Registry
from odoo import SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


class WechatAppController(http.Controller):

    @http.route('/api/wechat_category', type='http', auth="none", sitemap=False)
    def wechat_category(self, db_name):
        result = {}
        result['is_success'] = True
        cr = Registry(db_name).cursor()
        env = api.Environment(cr, SUPERUSER_ID, {})
        category_list = env['wechat.app.category'].sudo().get_categories()
        result['category_list'] = category_list
        if category_list and category_list[0]:
            app_list = env['wechat.app'].sudo().get_apps(category_list[0]["id"])
            result['current_app_list'] = app_list
            result['current_image_url'] = category_list[0]["thumb_url"]
            result['current_category_id'] = category_list[0]["id"]
            result['current_category_name'] = category_list[0]["name"]
            result['current_category_slogan'] = category_list[0]["slogan"]
        cr.close()
        return json.dumps(result)

    @http.route('/api/wechat_app', type='http', auth="none", sitemap=False)
    def wechat_app_list(self, db_name, category_id):
        result = {}
        result['is_success'] = True
        cr = Registry(db_name).cursor()
        env = api.Environment(cr, SUPERUSER_ID, {})
        app_list = env['wechat.app'].sudo().get_apps(category_id)
        category = env['wechat.app.category'].sudo().search([("id", "=", category_id)])
        result['current_app_list'] = app_list
        result['current_image_url'] = category.thumb_url
        result['current_category_id'] = category.id
        result['current_category_name'] = category.name
        result['current_category_slogan'] = category.slogan
        cr.close()
        return json.dumps(result)
