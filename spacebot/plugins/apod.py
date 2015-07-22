from datetime import datetime
import time
import logging

import re
import requests
from spacebot.util import utils

log = logging.getLogger(__name__)
APOD_BASE_URL = "http://apod.nasa.gov/"
APOD_PIX_URL = APOD_BASE_URL + "apod/astropix.html"
AUTHOR_NAME = "@apod"
AUTHOR_LINK = "https://twitter.com/apod"
AUTHOR_ICON = "https://pbs.twimg.com/profile_images/19829782/apod_normal.png"


# Gets the latest APOD using the NASA web API from https://api.nasa.gov/
def get_apod_data(api_key, date):
    r = requests.get("https://api.data.gov/nasa/planetary/apod", params={"api_key": api_key, "date": date})
    assert r.status_code == 200
    response = r.json()
    log.debug("APOD response: %s", response)
    return response


def get_apod_text_and_attachments(api_key, date=None):
    if not date:
        date = time.strftime("%Y-%m-%d")

    apod_data = get_apod_data(api_key, date)
    # The APOD API still returns a 200 in the error case, so we need
    # to handle it based on the actual message response data.
    if "error" in apod_data:
        title, text, image_url = "APOD Error", apod_data["error"], None
    else:
        title, text, image_url = apod_data["title"], apod_data["explanation"], apod_data["url"]
    attachments = {
        "title": title,
        "text": text,
        "image_url": image_url,
        "title_link": APOD_PIX_URL,
        "author_name": AUTHOR_NAME,
        "author_link": AUTHOR_LINK,
        "author_icon": AUTHOR_ICON
    }
    msg_text = "Astronomy Picture of the Day - " + datetime.strptime(date, "%Y-%m-%d").strftime("%a %B %d, %Y")
    return msg_text, attachments


def process_event(bot, event):
    command = event["text"].lower()
    if "apod" in command:
        search = re.search("apod (\w+.*)", command)
        if search:
            apod_date = search.group(1)
            try:
                utils.validate_date(apod_date)
            except ValueError:
                bot.send_message("Incorrect date format. Should be YYYY-MM-DD")
                return
            date = apod_date
        else:
            date = time.strftime("%Y-%m-%d")
        text, attachments = get_apod_text_and_attachments(bot.nasa_api_key, date)
        bot.send_message(text, attachments)


def get_help():
    return "*{name} APOD [YYYY-MM-DD]:* Displays the APOD for the given date (optional; defaults to today's APOD)."
