# -*- coding: utf-8 -*-
# Copyright (C) 2018 MAXSNS Corp (http://www.maxsns.com)
# @author Henry Zhou (zhouhenry@live.com)
# License OPL-1 - See https://www.odoo.com/documentation/user/11.0/legal/licenses/licenses.html

import werkzeug
import requests
from odoo import http, tools
from odoo.http import request
from odoo.service import security
import logging

_logger = logging.getLogger(__name__)
target_url = "https://api.weixin.qq.com/sns/jscode2session"


def ensure_db():
    db = request.params.get('db') and request.params.get('db').strip()

    # Ensure db is legit
    if db and db not in http.db_filter([db]):
        db = None

    if db and not request.session.db:
        # User asked a specific database on a new session.
        request.session.db = db
        return

    # if db not provided, use the session one
    if not db and request.session.db and http.db_filter([request.session.db]):
        db = request.session.db

    # if no database provided and no database in session, use monodb
    if not db:
        db = http.db_monodb(request.httprequest)

    # always switch the session to the computed db
    if db != request.session.db:
        request.session.logout()

    request.session.db = db


def _get_open_id(code, appid):
    secret = request.env['ir.config_parameter'].sudo().get_param('wechat.mp.secret.' + appid, '')
    if not secret:
        raise RuntimeError('Cannot get App Secret parameter for ' + appid)
    params = werkzeug.url_encode({
        "appid": appid, "secret": secret, "js_code": code, "grant_type": "authorization_code"
    })
    result = requests.get(target_url, params=params).json()
    if "openid" in result and result["openid"]:
        return result["openid"]
    elif "errcode" in result:
        raise RuntimeError(('WeChat Server Error: %s ' + result["errmsg"]) % result["errcode"])
    else:
        raise RuntimeError('Unknown WeChat Server Error')


def _set_session_info(uid, login):
    request.session.uid = uid
    request.session.login = login
    request.session.session_token = security.compute_session_token(request.session, request.env)
    request.uid = uid
    request.disable_db = False
    request.session.get_context()


def _get_session_info():
    return request.env["ir.http"].sudo().session_info()


class WeChatMiniProgramAuth(http.Controller):

    @http.route('/wechat_mp_auth/logout', type='json', auth="user")
    def logout(self, **kw):
        request.session.logout(keep_db=True)
        return True

    @http.route('/wechat_mp_auth/get_uid', type='json', auth="user", methods=["POST"])
    def get_uid(self, **kw):
        return {"uid": request.uid}

    @http.route('/wechat_mp_auth/auth_by_login', type='json', auth="none", methods=["POST"])
    def auth_by_login_third_part(self, code, appid, login, pwd, **kw):
        ensure_db()
        if login and pwd:
            account = request.env['wechat.mini.program.account'].sudo()
            '''try:
                uid = request.session.authenticate(request.session.db, login, pwd)
            except RuntimeError as ex:'''
            uid = account.check_third_part_login(login, pwd)
            if uid:
                try:
                    openid = _get_open_id(code, appid)
                except RuntimeError as e:
                    return {'error': 'wechat_error', 'message': '%s' % e}
                account.update_or_create_wechat_account_user(openid, appid, uid)
                _set_session_info(uid, login)
                return {'success': 'You have been logged in successfully!', 'session': _get_session_info()}
        return {'error': 'invalid_login', 'message': 'Invalid login name or password.'}

    @http.route('/wechat_mp_auth/auth_by_login_odoo', type='json', auth="none", methods=["POST"])
    def auth_by_login_odoo_part(self, code, appid, login, pwd, **kw):
        ensure_db()
        if login and pwd:
            account = request.env['wechat.mini.program.account'].sudo()
            try:
                uid = request.session.authenticate(request.session.db, login, pwd)
            except Exception as ex:
                info = tools.ustr(ex)
            if uid:
                try:
                    openid = _get_open_id(code, appid)
                except RuntimeError as e:
                    return {'error': 'wechat_error', 'message': '%s' % e}
                account.update_or_create_wechat_account_user(openid, appid, uid)
                _set_session_info(uid, login)
                return {'success': 'You have been logged in successfully!', 'session': _get_session_info()}
        return {'error': 'invalid_login', 'message': 'Invalid login name or password.'}

    @http.route('/wechat_mp_auth/auth_by_code', type='json', auth="none", methods=["POST"])
    def auth_by_code(self, code, appid, **kw):
        ensure_db()
        try:
            openid = _get_open_id(code, appid)
        except RuntimeError as e:
            return {'error': 'wechat_error', 'message': '%s' % e}
        account = request.env['wechat.mini.program.account'].sudo().search(
            [('wechat_open_id', '=', openid), ('wechat_app_id', '=', appid)])
        if account:
            _set_session_info(account.user_id.id, account.user_id.login)
            return {'success': 'You have been logged in successfully!', 'session': _get_session_info()}
        else:
            return {'error': 'auth_failed', 'message': 'Authenticating failed, login required.'}

    @http.route('/wechat_mp_auth/unauth_by_code', type='json', auth="user", methods=["POST"])
    def unauth_by_code(self, code, appid, **kw):
        ensure_db()
        try:
            openid = _get_open_id(code, appid)
        except RuntimeError as e:
            return {'error': 'wechat_error', 'message': '%s' % e}
        account = request.env['wechat.mini.program.account'].sudo().search(
            [('wechat_open_id', '=', openid), ('wechat_app_id', '=', appid)])
        if account:
            account.unlink()
            return {'success': 'You have been logged out successfully!'}
        else:
            return {'error': 'unauth_failed', 'message': 'UnAuthenticating failed'}

