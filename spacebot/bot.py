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
import time
import logging

import schedule
from docopt import docopt
from spacebot.apis import apod
from spacebot.apis import marsweather
from spacebot.slack import slackclient


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
        schedule.every().day.at(run_time).do(slackclient.send_message, token, channel,
                                             *apod.get_apod_text_and_attachments(key, date))
        schedule.every().day.at(run_time).do(slackclient.send_message, token, channel,
                                             *marsweather.get_weather_text_and_attachments())
        logging.info("SpaceBot successfully scheduled to run every day at %s", run_time)
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        slackclient.send_message(token, channel, *apod.get_apod_text_and_attachments(key, date))
        slackclient.send_message(token, channel, *marsweather.get_weather_text_and_attachments())
