import werkzeug
import json
import requests
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
        sql = """SELECT A.id, A.title, A.is_banner, A.category_id, A.create_date,B.Name,C.url
                      FROM news A left join news_category B 
                      on A.category_id = B.id 
                      left join ir_attachment C 
                      on A.id  =  C.res_id 
                      where A.is_banner  = %s 
                      and  A.is_publish = true 
                      and C.res_model='%s' 
              """
        banner_sql = sql % ("true", "news")
        news_sql = sql % ("false", "news")
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
        result['news_detail'] = env['news'].sudo().get_news_detail(news_id)
        cr.close()
        return json.dumps(result)
