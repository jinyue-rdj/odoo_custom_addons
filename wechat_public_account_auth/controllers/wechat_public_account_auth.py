
import hashlib
import six
import werkzeug
import requests
from odoo import http, tools
from odoo.http import request
from odoo.service import security
import logging

_logger = logging.getLogger(__name__)


class WeChatPublicAccountAuth(http.Controller):

    @http.route('/wechat_public_account_auth/validate', type='http', auth="none", methods=["GET"])
    def validate_auth(self, signature, timestamp, nonce, echostr, **kw):
        token = "guoodoo"  # 请按照公众平台官网\基本配置中信息填写
        list = [token, timestamp, nonce]
        list_data = []
        for data in list:
            list_data.append(self.to_binary(data))
        list_data.sort()
        _delimiter = self.to_binary(b'')
        str_to_sign = _delimiter.join(list_data)
        hashcode = hashlib.sha1(str_to_sign).hexdigest()
        if hashcode == signature:
            return echostr
        else:
            return ""

    def to_binary(self, value, encoding='utf-8'):
        """Convert value to binary string, default encoding is utf-8
        :param value: Value to be converted
        :param encoding: Desired encoding
        """
        if not value:
            return b''
        if isinstance(value, six.binary_type):
            return value
        if isinstance(value, six.text_type):
            return value.encode(encoding)

        return self.to_text(value).encode(encoding)

    def to_text(self, value, encoding='utf-8'):
        """Convert value to unicode, default encoding is utf-8
        :param value: Value to be converted
        :param encoding: Desired encoding
        """
        if not value:
            return ''
        if isinstance(value, six.text_type):
            return value
        if isinstance(value, six.binary_type):
            return value.decode(encoding)

        return six.text_type(value)
