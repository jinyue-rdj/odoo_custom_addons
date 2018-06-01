import json
from odoo import http, api
from odoo.modules.registry import Registry
from odoo import SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


class IndexController(http.Controller):

    @http.route('/api/wechat_index', type='http', auth="none", sitemap=False)
    def index_news_list(self, db_name):
        result = {}
        result['is_success'] = True
        sql = """SELECT A.id, A.title, A.is_banner, A.category_id, to_char(A.create_date,'yyyy-mm-dd') create_date,B.Name,C.url
                      FROM news A left join news_category B 
                      on A.category_id = B.id 
                      left join ir_attachment C 
                      on A.id  =  C.res_id 
                      where A.is_banner  = %s 
                      and  A.is_publish = true 
                      and C.res_model='%s' 
                      order by A.create_date desc
                      limit %d
              """
        banner_sql = sql % ("true", "news", 5)
        news_sql = sql % ("false", "news", 10)
        cr = Registry(db_name).cursor()
        env = api.Environment(cr, SUPERUSER_ID, {})
        env.cr.execute(banner_sql)
        result['banner_list'] = env.cr.dictfetchall()
        env.cr.execute(news_sql)
        result['news_list'] = env.cr.dictfetchall()
        cr.close()
        return json.dumps(result)

    @http.route('/api/wechat_new_detail', type='http', auth="none", sitemap=False)
    def get_news_detail(self, news_id, db_name):
        result = {}
        result['is_success'] = True
        cr = Registry(db_name).cursor()
        env = api.Environment(cr, SUPERUSER_ID, {})
        detail = env['news'].sudo().get_news_detail(news_id)
        result['news_detail'] = detail.content
        result['title'] = detail.title
        cr.close()
        return json.dumps(result)

    @http.route('/api/wechat_new_page', type='http', auth="none", sitemap=False)
    def index_news_list_page(self, db_name, page_index, page_size):
        result = {}
        result['is_success'] = True
        offset = (int(page_index)-1) * int(page_size)
        sql = """SELECT A.id, A.title, A.is_banner, A.category_id, to_char(A.create_date,'yyyy-mm-dd') create_date,B.Name,C.url
                      FROM news A left join news_category B 
                      on A.category_id = B.id 
                      left join ir_attachment C 
                      on A.id  =  C.res_id 
                      where A.is_publish = true 
                      and C.res_model='%s' 
                      order by A.create_date desc
                      limit %s offset %d
              """
        news_sql = sql % ("news", page_size, offset)
        cr = Registry(db_name).cursor()
        env = api.Environment(cr, SUPERUSER_ID, {})
        env.cr.execute(news_sql)
        result['news_list'] = env.cr.dictfetchall()
        cr.close()
        return json.dumps(result)
