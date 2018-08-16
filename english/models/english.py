
from odoo import fields, models, api
from bs4 import BeautifulSoup
import werkzeug
import requests
import logging

_logger = logging.getLogger(__name__)


class EnglishLexicon(models.Model):

    _name = 'english.lexicon'
    _description = 'english lexicon'

    word = fields.Char(string="Word", required=True, index=True)
    lexicon_explain_ids = fields.One2many('english.lexicon.explain', 'english_lexicon_id', "Detail")
    america_accent = fields.Char(string="America Accent")
    british_accent = fields.Char(string="British Accent")
    chinese_mean = fields.Text(string="Chinese Mean")
    america_voice_url = fields.Char(string="America URL")
    british_voice_url = fields.Char(string="British URL")
    source_name = fields.Char(string="From")
    sequence = fields.Integer()
    is_updated = fields.Boolean(string="Is Updated", default=False)
    forms = fields.Text(string="Word Forms")
    english_lexicon_synonymous_ids = fields.One2many('english.lexicon.synonymous', 'target_lexicon_id', "TargetSynonymous")

    @api.multi
    def name_get(self):
        return [(record.id, record.word) for record in self]


class EnglishLexiconExplain(models.Model):

    _name = 'english.lexicon.explain'
    _description = 'english lexicon explain'

    english_lexicon_id = fields.Many2one('english.lexicon', 'EnglishLexicon', ondelete='cascade', required=True)
    order = fields.Integer()
    raw_html_mean = fields.Text(string="Html Mean")
    gram = fields.Char(string="Gram")
    english_mean = fields.Text(string="Processed Mean")
    chinese_mean = fields.Text(string="Chinese Mean")
    is_format = fields.Boolean(string="Is Format", default=False)
    synonymous = fields.Text(string="Html Mean")
    lexicon_explain_example_ids = fields.One2many('english.lexicon.explain.example', 'english_lexicon_example_id', "Example")
    english_lexicon_synonymous_ids = fields.One2many('english.lexicon.synonymous', 'initial_explain_id', "Synonymous")


class EnglishLexiconExplainExample(models.Model):
    _name = "english.lexicon.explain.example"

    english_lexicon_example_id = fields.Many2one('english.lexicon.explain', 'EnglishLexiconExplain', ondelete='cascade', required=True)
    order = fields.Integer()
    sentence = fields.Text(string="Word Example")
    translate = fields.Text(string="Chinese Mean")
    is_translated = fields.Boolean(string="Is Translated", default=False)


class EnglishLexiconSynonymous(models.Model):
    _name = "english.lexicon.synonymous"

    initial_explain_id = fields.Many2one('english.lexicon.explain', 'EnglishLexiconExplain', ondelete='cascade', required=True)
    target_lexicon_id = fields.Many2one('english.lexicon', 'EnglishLexicon', ondelete='cascade', required=True)


class EnglishLexiconWordHtml(models.Model):
    _name = "english.lexicon.word.html"

    word = fields.Char(string="Word", required=True, index=True)
    html_content = fields.Html(string="Html")
    is_parsed = fields.Boolean(string="Is Parsed", default=False)
    america_accent = fields.Char(string="America Accent")
    british_accent = fields.Char(string="British Accent")
    chinese_mean = fields.Text(string="Chinese Mean")
    america_voice_url = fields.Char(string="America URL")
    british_voice_url = fields.Char(string="British URL")
    source_name = fields.Char(string="From")
    sequence = fields.Integer()
    try_count = fields.Integer(string="Try Count", default=0)

    def _automated_format_word(self):
        word_list = self.sudo().search([("is_parsed", "=", False), ("try_count", "<", "4")], limit=10)
        try:
            for word in word_list:
                _logger.info("word is %s", word.word)
                web_target_url = 'https://www.collinsdictionary.com/dictionary/english/' + word.word
                html = requests.get(web_target_url)
                learn = self.get_dictionary(html.text)
                chinese = self.get_chinese_mean(html.text)
                result = {"english": learn, "chinese": chinese, "html_raw": html.text}
                if "def_list" in result["english"]:
                    self.save_to_db(word, result)
                else:
                    word.write({
                        "html_content": html.text,
                        "try_count": word.try_count + 1
                    })
        except Exception:
            _logger.info("Parse word error")

    def get_chinese_mean(self, html):
        soup_all = BeautifulSoup(html, "lxml")
        translation_list = soup_all.select('.translation')
        result = []
        for trans in translation_list:
            mean_text = self.get_html_node_text(str(trans))
            if mean_text.startswith("Chinese:"):
                result.append(mean_text.strip("Chinese:").strip("\n").strip(" "))
        return result

    def get_dictionary(self, html):
        soup_all = BeautifulSoup(html, "lxml")
        learn_list = soup_all.select('.Cob_Adv_Brit')
        learn = {}
        if len(learn_list) > 0:
            dic = str(learn_list[0])
            word_def_list = self.extract_node_data(dic, "Learner")
            forms = self.extract_word_form(dic)
            learn = {"def_list": word_def_list, "form": forms}
        return learn

    def extract_word_form(self, html_dic):
        soup_all = BeautifulSoup(html_dic, "lxml")
        form_list = soup_all.select('.orth')
        form_result = []
        for form in form_list:
            form_result.append(self.get_html_node_text(str(form)))
        return form_result

    def extract_node_data(self, html_dic, part_name):
        word_definition = []
        soup_all = BeautifulSoup(html_dic, "lxml")
        hom_list = soup_all.select('.hom')
        for hom in hom_list:
            order_result = ""
            gram_result = ""
            def_result = ""
            cit_result = []
            synonymous = []
            soup = BeautifulSoup(str(hom), "lxml")
            orders = soup.select('.sensenum')
            grams = soup.select('.gramGrp')
            defs = soup.select('.def')
            cits = soup.select('.cit')
            thes = soup.select('.thes')
            if orders and len(orders) > 0:
                order_result = self.get_html_node_text(str(orders[0]))
                if order_result:
                    order_result = order_result.split(".")[0].strip(" ")
            if grams and len(grams) > 0:
                gram_result = self.get_html_node_text(str(grams[0]))
            if defs and len(defs) > 0:
                def_result = self.get_html_node_text(str(defs[0]))
            for cit in cits:
                cit_result.append(self.get_html_node_text(str(cit)))
            if thes and len(thes) > 0:
                soup_synonymous = BeautifulSoup(str(thes[0]), "lxml")
                form_list = soup_synonymous.select('.form')
                for form in form_list:
                    synonymous.append(self.get_html_node_text(str(form)))

            home_result = {
                "order": order_result,
                "english_explain": def_result,
                "gram": gram_result,
                "examples": cit_result,
                "synonymous": synonymous
            }
            word_definition.append(home_result)

        return word_definition

    def get_html_node_text(self, html):
        soup = BeautifulSoup(html, "lxml")
        return str(soup.get_text())

    def save_to_db(self, lexicon_word, data):
        explain_list = []
        for word_def in data["english"]["def_list"]:
            if word_def["english_explain"]:
                try:
                    order_id = int(word_def["order"])
                except Exception:
                    order_id = 1
                explain = (0, 0, {
                    "order": order_id,
                    "gram": word_def["gram"],
                    "english_mean": word_def["english_explain"],
                    "is_format": False,
                    "synonymous": ",".join(word_def["synonymous"]),
                    "lexicon_explain_example_ids": [(0, 0, {"order": index + 1, "sentence": x}) for index, x in
                                                    enumerate(word_def["examples"])]
                })
                explain_list.append(explain)

        if len(explain_list) > 0:
            self.env["english.lexicon"].create({
                "word": lexicon_word.word,
                "america_accent": lexicon_word.america_accent,
                "america_accent": lexicon_word.america_accent,
                "british_accent": lexicon_word.british_accent,
                "chinese_mean": lexicon_word.chinese_mean,
                "america_accent": lexicon_word.america_accent,
                "british_voice_url": lexicon_word.british_voice_url,
                "source_name": lexicon_word.source_name,
                "sequence": lexicon_word.sequence,
                "is_updated": True,
                "forms": ",".join(data["english"]["form"]),
                "lexicon_explain_ids": explain_list
            })

        lexicon_word.write({
            "html_content": data["html_raw"],
            "is_parsed": True
        })

    def update_try_count(self):
        _logger.info("begin try_count")
        sql = """ update english_lexicon_word_html set try_count = 0 """
        self.env.cr.execute(sql)


class EnglishLexiconExplainExample(models.Model):
    _name = "english.lexicon.master.level"

    name = fields.Text(string="Word Level")
    level_value = fields.Integer()
    enable = fields.Boolean(string="IsEnabled", default=True)

    def get_all_level(self):
        result = []
        list = self.search([('enable', '=', True)])
        for l in list:
            result.append({'name': l.name, 'id': l.id, 'value': l.level_value})
        return result


class EnglishLexiconExplainExample(models.Model):
    _name = "english.lexicon.user.master"

    english_lexicon_id = fields.Many2one('english.lexicon', 'EnglishLexicon', ondelete='cascade', required=True)
    user_id = fields.Many2one('res.users', 'User', ondelete='cascade', required=True)
    level_id = fields.Many2one("english.lexicon.master.level", string="Master Level", required=True)

    def save_user_word(self, word_id, user_id, level_id):
        word = self.search([('english_lexicon_id', '=', word_id), ('user_id', '=', user_id)], limit=1)
        if word:
            word.write({'level_id': level_id})
        else:
            self.create({'english_lexicon_id': word_id, 'user_id': user_id, 'level_id': level_id})

