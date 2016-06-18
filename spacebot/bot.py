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
import glob
import json
import time
import logging
import sys

import os
from docopt import docopt
import schedule
from slackclient import SlackClient
from spacebot import consts
from spacebot.plugins import apod


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
        self.plugins = self._load_plugins()

    def run(self):
        # Set up cron jobs
        if self.cron_time is not None:
            schedule.every().day.at(self.cron_time) \
                .do(lambda: self.send_message(*apod.get_apod_text_and_attachments(self.nasa_api_key)))

        # Initialize the WebSocket API connection
        if self.slack_client.rtm_connect():
            while True:
                try:
                    schedule.run_pending()
                    for event in self.slack_client.rtm_read():
                        self.log.debug("Received event: %s", str(event))
                        self._process_event(event)
                    time.sleep(0.5)
                except Exception, e:
                    self.log.error("Unexpected exception %s", e)
                    self.send_message("Something killed me :(")
                    sys.exit(1)
        else:
            self.log.error("Slack connection failed")

    def send_message(self, text, attachments=None):
        self.slack_client.api_call("chat.postMessage",
                                   username=consts.SPACEBOT_USERNAME,
                                   icon_url=consts.SPACEBOT_ICON_URL,
                                   channel=self.channel,
                                   text=text,
                                   attachments=json.dumps([attachments]))

    def _load_plugins(self):
        module_file_names = glob.glob(os.path.dirname(__file__) + "/plugins/*.py")
        module_names = [os.path.basename(f)[:-3] for f in module_file_names[1:]]
        plugins_package = __import__("spacebot.plugins", fromlist=module_names)
        return map(lambda name: getattr(plugins_package, name), module_names)

    def _process_event(self, event):
        # For whatever reason, Slack sends empty events, so we need to ignore them
        if not event:
            return

        # Ignore events that aren't messages addressing SpaceBot
        if event["type"] != "message" \
                or "subtype" in event \
                or ("channel" in event and event["channel"] != self.channel) \
                or ("text" in event and not event["text"].lower().startswith(consts.SPACEBOT_USERNAME.lower())):
            return

        self.log.info("Received message: %s", str(event))
        if "help" in event["text"].lower():
            help_msgs = "\n".join([plugin.get_help() for plugin in self.plugins if hasattr(plugin, "get_help")])
            text = ("Available commands (case insensitive):\n\n*{name} help: Shows this." + help_msgs) \
                .format(name=consts.SPACEBOT_USERNAME)
            self.send_message(text)
        elif "open the pod bay doors" in event["text"].lower():
            user = json.loads(self.slack_client.api_call("users.info", user=event["user"]))["user"]
            name = user["profile"]["first_name"]
            self.send_message("I'm sorry {name}. I'm afraid I can't do that.".format(name=name))
        elif "still alive" in event["text"].lower():
            self.send_message("Yes")
        else:
            for plugin in self.plugins:
                try:
                    plugin.process_event(self, event)
                except AttributeError:
                    pass
