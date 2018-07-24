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
        word_list = request.env['english.lexicon'].sudo().search([
            "|",
            ("word", "ilike", key),
            ("chinese_mean", "ilike", key)])
        for word in word_list:
            result = {"word": word.word,
                      "chinese_mean": word.chinese_mean,
                      "british_accent": word.british_accent,
                      "source_name": word.source_name,
                      "sequence": word.sequence,
                      "forms": word.forms,
                      }
            defintion_list = []
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

            special_defintion_word = {
                "order": 0,
                "gram": "",
                "english_mean": word.chinese_mean,
                "chinese_mean": "",
                "synonymous": word.forms,
                "sentence_list": []
            }
            defintion_list.append(special_defintion_word)
            defintion_list.append(defintion_word)
            result["defintion_list"] = defintion_list
            result_list.append(result)
            #_logger.info("result is %s", result_list)
        return result_list
