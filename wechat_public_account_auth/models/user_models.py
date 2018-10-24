# coding=utf-8

import logging
from odoo import models, fields, api
from odoo.http import request

_logger = logging.getLogger(__name__)


class wx_user(models.Model):
    _name = 'wx.user'
    _description = u'公众号用户'

    city = fields.Char(u'城市', )
    country = fields.Char(u'国家', )
    group_id = fields.Selection('_get_groups', string=u'所属组', default='0')
    headimgurl = fields.Char(u'头像', )
    nickname = fields.Char(u'昵称', )
    openid = fields.Char(u'用户标志', )
    province = fields.Char(u'省份', )
    sex = fields.Selection([(1, u'男'), (2, u'女')], string=u'性别', )
    subscribe = fields.Boolean(u'关注状态', )
    subscribe_time = fields.Char(u'关注时间', )

    headimg= fields.Html(compute='_get_headimg', string=u'头像')
    last_uuid = fields.Char('会话ID')
    user_id = fields.Many2one('res.users', '关联本系统用户')


    @api.one
    def _get_headimg(self):
        self.headimg= '<img src=%s width="100px" height="100px" />' % (self.headimgurl or '/web/static/src/img/placeholder.png')

    def _get_groups(self):
        Group = self.env['wx.user.group']
        objs = Group.search([])
        return [(str(e.group_id), e.group_name) for e in objs] or [('0', '默认组')]


class wx_user_group(models.Model):
    _name = 'wx.user.group'
    _description = u'公众号用户组'

    count = fields.Integer(u'用户数', )
    group_id = fields.Integer(u'组编号', )
    group_name = fields.Char(u'组名', )
    user_ids = fields.One2many('wx.user', 'group_id', u'用户', )


class wx_corpuser(models.Model):
    _name = 'wx.corpuser'
    _description = u'企业号用户'

    name = fields.Char('昵称', required=True)
    userid = fields.Char('账号', required=True)
    avatar = fields.Char('头像', )
    position = fields.Char('职位', )
    gender = fields.Selection([(1, '男'), (2, '女')], string='性别', )
    weixinid = fields.Char('微信号', )
    mobile = fields.Char('手机号',)
    email = fields.Char('邮箱',)
    status = fields.Selection([(1, '已关注'), (2, '已禁用'), (4, '未关注')], string='状态', default=4)
    extattr = fields.Char('扩展属性', )

    avatarimg= fields.Html(compute='_get_avatarimg', string=u'头像')
    last_uuid = fields.Char('会话ID')

    _sql_constraints = [
        ('userid_key', 'UNIQUE (userid)',  '账号已存在 !'),
        ('email_key', 'UNIQUE (email)',  '邮箱已存在 !'),
        ('mobile_key', 'UNIQUE (mobile)',  '手机号已存在 !')
    ]

    @api.one
    def _get_avatarimg(self):
        self.avatarimg = '<img src=%s width="100px" height="100px" />' % (self.avatar or '/web/static/src/img/placeholder.png')

