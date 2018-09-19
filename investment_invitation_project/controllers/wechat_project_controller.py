from odoo import http, tools
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class WechatProjectController(http.Controller):

    @http.route('/api/v2/wechat_invest_projects', type='json', auth="user")
    def wechat_get_projects(self, page_index, page_size, key_project, **kw):
        result = {'is_success': True}
        try:
            data = request.env['invest.project'].sudo().get_project_list(page_index, page_size, key_project)
            result['data'] = data
        except Exception as e:
            result = {'is_success': False, 'info': tools.ustr(e)}
        return result

    @http.route('/api/v2/wechat_follow_project', type='json', auth="user")
    def wechat_follow_project(self, project_id, **kw):
        user_id = request.env.user.id
        result = {'is_success': True}
        try:
            request.env['invest.project'].sudo().follow_project(project_id, user_id)
        except Exception as e:
            result = {'is_success': False, 'info': tools.ustr(e)}
        return result

    @http.route('/api/v2/wechat_comment', type='json', auth="user")
    def wechat_save_comment(self, project_id, content, **kw):
        user_id = request.env.user.id
        result = {'is_success': True}
        try:
            request.env['invest.project.comment'].sudo().save_user_comment(project_id, user_id, content)
        except Exception as e:
            result = {'is_success': False, 'info': tools.ustr(e)}
        return result

    @http.route('/api/v2/wprojects', type='json', auth="user")
    def wechat_get_my_follow_projects(self, page_index, page_size, **kw):
        user_id = request.env.user.id
        result = {'is_success': True}
        try:
            data = request.env['invest.project'].sudo().get_follow_projects(page_index, page_size, user_id)
            result['data'] = data
        except Exception as e:
            result = {'is_success': False, 'info': tools.ustr(e)}
        return result

    @http.route('/api/v2/wechat_my_projects', type='json', auth="user")
    def wechat_get_my_projects(self, page_index, page_size, **kw):
        user_id = request.env.user.id
        result = {'is_success': True}
        try:
            data = request.env['invest.project'].sudo().get_my_projects(page_index, page_size, user_id)
            result['data'] = data
        except Exception as e:
            result = {'is_success': False, 'info': tools.ustr(e)}
        return result

    @http.route('/api/v2/wechat_month_or_week_projects', type='json', auth="user")
    def wechat_get_my_projects(self, page_index, page_size, month_or_week, **kw):
        result = {'is_success': True}
        try:
            data = request.env['invest.project'].sudo().get_project_list_by_month_or_week(page_index, page_size, month_or_week)
            result['data'] = data
        except Exception as e:
            result = {'is_success': False, 'info': tools.ustr(e)}
        return result

