# coding=utf-8
import logging

from ..ext_libs.werobot.client import Client, ClientException
from ..ext_libs.werobot.robot import BaseRoBot
from ..ext_libs.werobot.session.memorystorage import MemoryStorage
from ..ext_libs.werobot.logger import enable_pretty_logging

_logger = logging.getLogger(__name__)


class WechatOdooRoBot(BaseRoBot):
    pass


WechatOdooRoBot.message_types.append('file')


WxEnvDict = {}


class WxEntry(object):

    def __init__(self):
        config = {"APP_ID": "appid_xxx", "APP_SECRET": "appsecret_xxxx"}
        self.wxclient = Client(config)
        self.UUID_OPENID = {}
        self.OPENID_UUID = {}
        self.robot = None

    def init(self, env):
        dbname = env.cr.dbname
        global WxEnvDict
        if dbname in WxEnvDict:
            del WxEnvDict[dbname]
        WxEnvDict[dbname] = self

        param = env['ir.config_parameter'].sudo()
        self.wx_token = param.get_param('wx_token') or ''
        self.wx_appid = param.get_param('wx_appid') or ''
        self.wx_AppSecret = param.get_param('wx_AppSecret') or ''

        self.wxclient.config = {"APP_ID": self.wx_appid, "APP_SECRET": self.wx_AppSecret}

        try:
            self.wxclient._token = None
            _ = self.wxclient.token
        except Exception:
            import traceback
            traceback.print_exc()
            _logger.error(u'初始化微信客户端token失败，请在微信对接配置中填写好相关信息！')

        session_storage = MemoryStorage()
        robot = WechatOdooRoBot(token=self.wx_token,logger=_logger,enable_session=True,session_storage=session_storage,app_id=self.wx_appid,app_secret=self.wx_AppSecret)
        enable_pretty_logging(robot.logger)
        self.robot = robot

        '''try:
            users = env['wx.user'].sudo().search([('last_uuid', '!=', None)])
            for obj in users:
                self.OPENID_UUID[obj.openid] = obj.last_uuid
                self.UUID_OPENID[obj.last_uuid] = obj.openid
        except Exception:
            env.cr.rollback()
            import traceback
            traceback.print_exc()'''

        print('wx client init: %s %s' % (self.OPENID_UUID, self.UUID_OPENID))


def wxenv(env):
    return WxEnvDict[env.cr.dbname]
