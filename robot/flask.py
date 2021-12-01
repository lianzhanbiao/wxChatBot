# -*- coding: utf-8 -*-

from flask import request, make_response

import html


def make_view(robot):
    def werobot_view():
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        signature = request.args.get('signature', '')
        if not robot.check_signature(
            timestamp,
            nonce,
            signature,
        ):
            return robot.make_error_page(html.escape(request.url)), 403
        if request.method == 'GET':
            return request.args['echostr']

        message = robot.parse_message(
            request.data,
            timestamp=timestamp,
            nonce=nonce,
            msg_signature=request.args.get('msg_signature', '')
        )
        response = make_response(robot.get_reply(message))
        response.headers['content_type'] = 'application/xml'
        return response

    return werobot_view
