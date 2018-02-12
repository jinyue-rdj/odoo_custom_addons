
from odoo import fields, models


class EnglishLexicon(models.Model):

    _name = 'english.lexicon'
    _description = 'english lexicon'

    word = fields.Char(string="Word", required=True, index=True)
    america_accent = fields.Char(string="America Accent")
    british_accent = fields.Char(string="British Accent")
    chinese_mean = fields.Text(string="Chinese Mean")
    html_mean = fields.Text(string="Html Mean")
    html_raw_content = fields.Text(string="Html Content")
    america_voice_url = fields.Char(string="America URL")
    british_voice_url = fields.Char(string="British URL")
    source_name = fields.Char(string="From")
    sequence = fields.Integer()
    is_updated = fields.Boolean(string="Is Updated", default=False)

