from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


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


class WechatIndexController(http.Controller):

    @http.route('/api/v2/wechat_list', type='json', auth="user", sitemap=False)
    def index_news_list(self, **kw):
        ensure_db()
        result = request.env["news"].sudo().get_list()
        return result

    @http.route('/api/v2/wechat_new_detail', type='json', auth="user", sitemap=False)
    def get_news_detail(self, news_id, **kw):
        ensure_db()
        result = {}
        result['is_success'] = True
        detail = request.env['news'].sudo().get_news_detail(news_id)
        result['news_detail'] = detail.content
        result['title'] = detail.title
        return result

    @http.route('/api/v2/wechat_new_page', type='json', auth="user", sitemap=False)
    def index_news_list_page(self, page_index, page_size, **kw):
        ensure_db()
        result = request.env['news'].sudo().get_list_page(page_index, page_size)
        return result
