
import os
import werkzeug
import requests
import logging
from odoo import http, tools
from odoo.http import request
from . import client
from .handlers import sys_event
from .handlers import menu_click
from ..ext_libs.werobot.replies import process_function_reply
_logger = logging.getLogger(__name__)


def abort(code):
    return werkzeug.wrappers.Response('Unknown Error: Application stopped.',
                                      status=code,
                                      content_type='text/html;charset=utf-8')


class WeChatPublicAccountHandler(http.Controller):

    def __init__(self):
        entry = client.WxEntry()
        entry.init(request.env)
        robot = entry.robot
        self.robot = robot
        sys_event.main(robot)
        menu_click.main(robot)

    @http.route('/wechat_public_account_handler', type='http', auth="none", methods=["GET"])
    def validate_auth(self, signature, timestamp, nonce, echostr, **kw):
        if not self.robot.check_signature(timestamp, nonce, signature):
            return abort(403)
        return echostr

    @http.route('/wechat_public_account_handler', type='http', auth="none", methods=["POST"])
    def handler(self, **kw):
        timestamp = request.params.get("timestamp")
        nonce = request.params.get("nonce")
        signature = request.params.get("signature")

        body = request.httprequest.data
        message = self.robot.parse_message(body, timestamp, nonce, signature)
        self.robot.logger.info("Receive message %s" % message)
        reply = self.robot.get_reply(message)
        if not reply:
            self.robot.logger.warning("No handler responded message %s" % message)
            return ''
        return process_function_reply(reply, message=message)
