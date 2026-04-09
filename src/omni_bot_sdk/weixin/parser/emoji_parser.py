#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time        : 2024/12/12 18:10
@Author      : SiYuan
@Email       : 863909694@qq.com
@File        : MemoTrace-emoji_parser.py
@Description : 表情包解析
"""
import base64
import html
import re

import xmltodict
from google.protobuf.json_format import MessageToDict

from .util.protocbuf import emoji_desc_pb2


def parser_emoji(xml_content):
    result = {"md5": "", "url": "", "width": 0, "height": 0, "desc": ""}

    def extract_msg(text):
        pattern = r"(<msg>.*?</msg>)"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(0) if match else ""

    xml_dict = {}
    try:
        xml_dict = xmltodict.parse(xml_content)
    except Exception:
        try:
            xml_content = extract_msg(xml_content)
            xml_dict = xmltodict.parse(xml_content)
        except Exception:
            return result

    try:
        emoji_dic = xml_dict.get("msg", {}).get("emoji", {})

        # 获取 md5
        md5 = emoji_dic.get("@androidmd5") or emoji_dic.get("@md5", "")

        # 获取 desc (protobuf解析)
        desc = ""
        desc_bs64 = emoji_dic.get("@desc", "")
        if desc_bs64:
            try:
                desc_bytes_proto = base64.b64decode(desc_bs64)
                message = emoji_desc_pb2.EmojiDescData()
                message.ParseFromString(desc_bytes_proto)
                dict_output = MessageToDict(message)
                for item in dict_output.get("descItem", []):
                    desc = item.get("desc", "")
                    if desc:
                        break
            except Exception:
                pass

        # 获取 url
        url = emoji_dic.get("@cdnurl", "")
        if url:
            url = html.unescape(url)

        result = {
            "md5": md5,
            "url": url,
            "width": int(emoji_dic.get("@width", 0)),
            "height": int(emoji_dic.get("@height", 0)),
            "desc": desc,
        }
    except Exception:
        pass

    return result