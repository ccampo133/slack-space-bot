"""Usage:
  spacebot (-c CHANNEL) (-t TOKEN) [-k KEY] [-d DATE] [-T TIME] [-f LOGFILE] [-l LEVEL]
  spacebot (-h | --help)

  Options:
  -c CHANNEL --chan=CHANNEL   The Slack channel or group ID.
  -t TOKEN --token=TOKEN      Your Slack API token.
  -k --key=KEY                Your NASA API key (apply for one at https://data.nasa.gov/developer/external/planetary/#apply-for-an-api-key)
                              [default: DEMO_KEY].
  -d --date=DATE              The date of the APOD you want to retrieve (format: YYYY-MM-dd) [default: today]
  -T --time=TIME              The time of day to run (in 24 hour format HH:mm, e.g. 11:00). Ignoring
                              this option will cause SpaceBot to run now, and only once.
  -f --file=LOGFILE           The file to output all logging info. [default: spacebot.log]
  -l --level=LEVEL            The logging level: DEBUG, INFO, WARNING, ERROR, or CRITICAL. [default: INFO]
  -h --help                   Show this screen.
"""
from datetime import datetime
import time
import logging
import json

import schedule
import requests
from docopt import docopt


slack_base_url = "https://slack.com/api/"
apod_base_url = "http://apod.nasa.gov/"
apod_pix_url = apod_base_url + "apod/astropix.html"
author_name = "@apod"
author_link = "https://twitter.com/apod"
author_icon = "https://pbs.twimg.com/profile_images/19829782/apod_normal.png"
spacebot_icon_url = "http://i.imgur.com/xm4a5PP.jpg"


def main():
    args = docopt(__doc__)
    key = args["--key"]
    token = args["--token"]
    date = time.strftime("%Y-%m-%d") if args["--date"] == "today" else args["--date"]
    channel = args["--chan"]
    run_time = args["--time"]
    log_file = args["--file"]
    log_level = args["--level"]

    # Set up logging stuff
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % log_level)
    logging.basicConfig(filename=log_file, level=numeric_level,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logging.getLogger().addHandler(logging.StreamHandler())  # Add logger to stderr

    if run_time is not None:
        schedule.every().day.at(run_time).do(send_message, token, key, channel, date)
        logging.info("SpaceBot successfully scheduled to run every day at %s", run_time)
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        send_message(token, key, channel, date)


def get_apod_data(key, date):
    r = requests.get("https://api.data.gov/nasa/planetary/apod", params={"api_key": key, "date": date})
    assert r.status_code == 200
    response = r.json()
    logging.debug("APOD response: %s", response)
    return response


def send_message(token, key, channel, date):
    apod_data = get_apod_data(key, date)

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
        "title_link": apod_pix_url,
        "author_name": author_name,
        "author_link": author_link,
        "author_icon": author_icon
    }

    msg_data = {
        "token": token,
        "channel": channel,
        "text": "Astronomy Picture of the Day - " + datetime.strptime(date, "%Y-%m-%d").strftime("%a %B %d, %Y"),
        "username": "SpaceBot",
        "icon_url": spacebot_icon_url,
        "attachments": json.dumps([attachments])
    }

    r = requests.post(slack_base_url + "chat.postMessage", msg_data)
    logging.info("Sent message with data: %s", msg_data)
    assert r.status_code == 200
