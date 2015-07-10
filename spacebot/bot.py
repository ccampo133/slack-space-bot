"""Usage:
  spacebot (-c CHANNEL) (-t TOKEN) [-k KEY] [-T TIME] [-f LOGFILE] [-l LEVEL]
  spacebot (-h | --help)

  Options:
  -c CHANNEL --chan=CHANNEL   The Slack channel or group ID.
  -t TOKEN --token=TOKEN      Your Slack API token.
  -k --key=KEY                Your NASA API key (apply for one at https://data.nasa.gov/developer/external/planetary/#apply-for-an-api-key)
                              [default: DEMO_KEY].
  -T --apod-time=TIME         The time of day to post automatically post APOD (in 24 hour format HH:mm, e.g. 11:00).
  -f --file=LOGFILE           The file to output all logging info. [default: spacebot.log]
  -l --level=LEVEL            The logging level: DEBUG, INFO, WARNING, ERROR, or CRITICAL. [default: INFO]
  -h --help                   Show this screen.
"""
import json
import time
import logging
import sys

import re
from docopt import docopt
import schedule
from slackclient import SlackClient
from spacebot import consts
from spacebot.apis import apod
from spacebot.apis import marsweather
from spacebot.apis import iss


def main():
    args = docopt(__doc__)
    channel = args["--chan"]
    token = args["--token"]
    key = args["--key"]
    apod_time = args["--apod-time"]
    log_file = args["--file"]
    log_level = args["--level"]

    # Set up logging stuff
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % log_level)
    logging.basicConfig(filename=log_file, level=numeric_level,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logging.getLogger().addHandler(logging.StreamHandler())  # Add logger to stderr

    # Start the bot
    slack = SlackClient(token)
    bot = SpaceBot(slack, channel, key, apod_time)
    try:
        bot.run()
    except KeyboardInterrupt:
        sys.exit(0)


class SpaceBot:
    def __init__(self, slack_client, channel, nasa_api_key, cron_time):
        self.log = logging.getLogger(__name__)
        self.slack_client = slack_client
        self.channel = channel
        self.nasa_api_key = nasa_api_key
        self.cron_time = cron_time

    def run(self):
        # Set up cron jobs
        if self.cron_time is not None:
            schedule.every().day.at(self.cron_time).do(self.send_message,
                                                       *apod.get_apod_text_and_attachments(self.nasa_api_key,
                                                                                           time.strftime("%Y-%m-%d")))
        # Initialize the WebSocket API connection
        if self.slack_client.rtm_connect():
            while True:
                schedule.run_pending()
                for event in self.slack_client.rtm_read():
                    self.process(event)
                time.sleep(0.5)
        else:
            self.log.error("Slack connection failed")

    def process(self, event):
        # Ignore events that aren't messages addressing SpaceBot
        if event["type"] != "message" \
                or event["channel"] != self.channel \
                or not event["text"].lower().startswith(consts.SPACEBOT_USERNAME.lower()):
            return

        command = re.sub(consts.SPACEBOT_USERNAME.lower(), "", event["text"].lower()).lstrip()
        self.log.info("Message: %s", str(event))
        self.log.info("Command: %s", command)

        if command.startswith("apod"):
            apod_date = re.sub("apod", "", command).lstrip()
            date = time.strftime("%Y-%m-%d") if not apod_date else apod_date
            text, attachments = apod.get_apod_text_and_attachments(self.nasa_api_key, date)
            self.send_message(text, attachments)
        elif command == "mars weather":
            text, attachments = marsweather.get_weather_text_and_attachments()
            self.send_message(text, attachments)
        elif command == "iss":
            text, attachments = iss.get_iss_text_and_attachments()
            self.send_message(text, attachments)
        elif command == "help":
            self.send_help_message()
        else:
            user = json.loads(self.slack_client.api_call("users.info", user=event["user"]))["user"]
            name = user["profile"]["first_name"]
            self.send_message("I'm sorry {name}. I'm afraid I can't do that.".format(name=name))

    def send_message(self, text, attachments=None):
        self.slack_client.api_call("chat.postMessage",
                                   username=consts.SPACEBOT_USERNAME,
                                   icon_url=consts.SPACEBOT_ICON_URL,
                                   channel=self.channel,
                                   text=text,
                                   attachments=json.dumps([attachments]))

    def send_help_message(self):
        text = "Available commands (case insensitive):\n\n" \
               "*{name} APOD [YYYY-MM-DD]:* Displays the APOD for the given date (optional; defaults to today's APOD)\n" \
               "*{name} ISS:* Displays information about the current location of the International Space Station.\n" \
               "*{name} Mars Weather:* Displays the current Martian weather report from the Curiosity rover\n" \
               "*{name} help:* Shows this.".format(name=consts.SPACEBOT_USERNAME)
        self.send_message(text)
