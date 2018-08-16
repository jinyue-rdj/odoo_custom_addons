from odoo import http
from odoo.http import request
from bs4 import BeautifulSoup
import werkzeug
import requests
import logging

_logger = logging.getLogger(__name__)


class WechatEnglishController(http.Controller):

    @http.route('/api/v2/wechat_english', type='json', auth="user")
    def wechat_category(self, key, **kw):
        result_list = []
        user_id = request.env.user.id
        user_word = request.env['english.lexicon.user.master']
        word_list = request.env['english.lexicon'].sudo().search([
            "|",
            ("word", "ilike", key),
            ("chinese_mean", "ilike", key)])
        for word in word_list:
            is_added = False
            user_master = user_word.sudo().search([('english_lexicon_id', '=', word.id), ('user_id', '=', user_id)], limit=1)
            if user_master:
                is_added = True
            result = {"id": word.id,
                      "word": word.word,
                      "chinese_mean": word.chinese_mean,
                      "british_accent": word.british_accent,
                      "source_name": word.source_name,
                      "sequence": word.sequence,
                      "forms": word.forms,
                      "is_added": is_added
                      }
            defintion_list = []
            special_defintion_word = {
                "order": 0,
                "gram": "",
                "english_mean": word.chinese_mean,
                "chinese_mean": "",
                "synonymous": word.forms,
                "sentence_list": []
            }
            defintion_list.append(special_defintion_word)

            for defintion in word.lexicon_explain_ids:
                defintion_word = {
                    "order": defintion.order,
                    "gram": defintion.gram,
                    "english_mean": defintion.english_mean,
                    "chinese_mean": defintion.chinese_mean,
                    "synonymous": defintion.synonymous,
                }
                sentence_list = []
                for example in defintion.lexicon_explain_example_ids:
                    sentences = {
                    "order": example.order,
                    "example": example.sentence,
                    }
                    sentence_list.append(sentences)
                defintion_word["sentence_list"] = sentence_list

                defintion_list.append(defintion_word)

            result["defintion_list"] = defintion_list
            result_list.append(result)
        return result_list

    @http.route('/api/v2/wechat_english_level', type='json', auth="user")
    def get_word_level_list(self, **kwargs):
        return request.env['english.lexicon.master.level'].sudo().get_all_level()

    @http.route('/api/v2/wechat_english_save', type='json', auth="user")
    def get_word_level_save(self, word_id, level_id, **kwargs):
        result = {'is_success': True}
        user_id = request.env.user.id
        try:
            request.env['english.lexicon.user.master'].sudo()\
                .save_user_word(word_id, user_id, level_id)
        except Exception:
            result['is_success'] = False
        return result
