"""Usage:
  spacebot (-c CHANNEL) (-t TOKEN) [-T TIME] [-f LOGFILE] [-l LEVEL]
  spacebot (-h | --help)

  Options:
  -c CHANNEL --chan=CHANNEL   The Slack channel or group ID.
  -t TOKEN --token=TOKEN      Your Slack API token.
  -T --time=TIME              The time of day to run (in 24 hour format HH:mm, e.g. 11:00). [default: 12:00]
  -f --file=LOGFILE           The file to output all logging info. [default: spacebot.log]
  -l --level=LEVEL            The logging level: DEBUG, INFO, WARNING, ERROR, or CRITICAL. [default: INFO]
  -h --help                   Show this screen.
"""
import json
import urllib2
import datetime
import time
import logging

import re
import schedule
from docopt import docopt
from slacker import Slacker
from bs4 import BeautifulSoup


apod_base_url = 'http://apod.nasa.gov/'
apod_pix_url = apod_base_url + 'apod/astropix.html'
author_name = '@apod'
author_link = 'https://twitter.com/apod'
author_icon = 'https://pbs.twimg.com/profile_images/19829782/apod_normal.png'
spacebot_icon_url = 'http://i.imgur.com/xm4a5PP.jpg'


def get_apod_data():
    response = urllib2.urlopen(apod_pix_url)
    html = response.read()
    soup = BeautifulSoup(html)
    title = soup.b.string
    img_url = apod_base_url + str(soup.img['src'])
    text = re.findall('Explanation:(.*?)Tomorrow', soup.get_text(), re.DOTALL | re.MULTILINE)[0]
    text = text.replace('\n', ' ').rstrip().lstrip()
    text = re.sub("\s\s+", " ", text)  # removes double spaces
    logging.debug('title = %s, img_url = %s, text = %s' % (title, img_url, text))
    return title, img_url, text


def send_message(slack_client, chan):
    title, img_url, text = get_apod_data()
    attachments = json.dumps([
        {
            'title': title,
            'text': text,
            'image_url': img_url,
            'title_link': apod_pix_url,
            'author_name': author_name,
            'author_link': author_link,
            'author_icon': author_icon
        }
    ])
    msg_title = 'Astronomy Picture of the Day - ' + datetime.datetime.now().strftime("%a %B %d, %Y")
    slack_client.chat.post_message(chan, msg_title, username='SpaceBot', icon_url=spacebot_icon_url,
                                   attachments=attachments)
    logging.info('Sent message: chan = %s, msg_title = %s, attachments = %s' % (chan, msg_title, attachments))


if __name__ == '__main__':
    args = docopt(__doc__)
    token = args['--token']
    channel = args['--chan']
    run_time = args['--time']
    log_file = args['--file']
    log_level = args['--level']

    # Set up logging stuff
    # TODO - add timestamps and more advanced logging configuration
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)
    logging.basicConfig(filename=log_file, level=numeric_level)

    slack = Slacker(token)  # Slack client (using the 'Slacker' library)
    schedule.every().day.at(run_time).do(send_message, slack, channel)

    logging.info("SpaceBot is scheduled to run every day at %s" % run_time)
    while True:
        schedule.run_pending()
        time.sleep(1)
