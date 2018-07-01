# -*- coding: utf-8 -*-
{
    'name': "form button and fields control",

    'summary': """
        Set one parameter to show or hide form edit button.
        Set some readonly fields in form view and check in orm write function. 
        """,

    'description': """
        the module has two functions. the first is used for controlling the edit button to be show or hide
        according to the vale which is set in db.
        the second is to set some readonly fields for one model when the state field is some special value
    """,

    'author': "Huanhuan Guo",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web'],

    # always loaded
    'data': [
        'views/templates.xml',
        'views/model_state_group_permission.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}