import json
import logging

import requests
from spacebot import consts

log = logging.getLogger(__name__)


def send_message(token, channel, text, attachments=None):
    msg_data = {
        "token": token,
        "channel": channel,
        "text": text,
        "username": consts.SPACEBOT_USERNAME,
        "icon_url": consts.SPACEBOT_ICON_URL
    }
    if attachments is not None:
        msg_data["attachments"] = json.dumps([attachments])
    r = requests.post(consts.SLACK_BASE_URL + "chat.postMessage", msg_data)
    log.info("Sent Slack message with data: %s", msg_data)
    assert r.status_code == 200
