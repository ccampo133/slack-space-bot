"""Usage:
  spacebot (-c CHANNEL) (-t TOKEN) (-T TIME)
  spacebot (-h | --help)

  Options:
  -c CHANNEL --channel=CHANNEL    The Slack channel/group ID.
  -t TOKEN --token=TOKEN          Your Slack API token
  -T --time=TIME                  The time of day to run (in 24 hour format HH:mm, e.g. 11:00)
  -h --help                       Show this screen.
"""
import json
import urllib2
import datetime
import time

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
    return title, img_url, text


def send_message(slack_client, chan):
    title, text, img_url = get_apod_data()
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
    print(title, text, img_url, attachments)
    msg_title = 'Astronomy Picture of the Day - ' + datetime.datetime.now().strftime("%a %B %d, %Y")
    slack_client.chat.post_message(chan, msg_title, username='SpaceBot', icon_url=spacebot_icon_url,
                                   attachments=attachments)


if __name__ == '__main__':
    args = docopt(__doc__)
    token = args['--token']
    channel = args['--channel']
    run_time = args['--time']
    slack = Slacker(token)  # Slack client (using the 'Slacker' library)

    schedule.every().day.at(run_time).do(send_message, slack, channel)

    while True:
        schedule.run_pending()
        time.sleep(1)
