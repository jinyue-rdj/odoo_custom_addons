# -*- coding: utf-8 -*-

{
    'name': 'English',
    'sequence': 170,
    'version': '1.0',
    'depends': ['base', 'web', 'decimal_precision'],
    'category': 'Study',
    'summary': 'English words,sentences',
    'description': """
The base module to manage english words for non-native speakers.
================================
The app uses english sentences to explain the words meaning.
    """,
    'data': [
        'security/english_security.xml',
        'security/ir.model.access.csv',
        'views/english_views.xml',
        'data/format_word_cron.xml',
    ],
    'installable': True,
    'application': True,
}
