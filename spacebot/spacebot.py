"""Usage:
  spacebot (-c CHANNEL) (-t TOKEN)
  spacebot (-h | --help)

  Options:
  -c CHANNEL --channel=CHANNEL    The Slack channel/group ID.
  -t TOKEN --token TOKEN          Your Slack API token
  -h --help                       Show this screen.
"""
import json
import urllib2
import datetime
import re

from docopt import docopt
from slacker import Slacker
from bs4 import BeautifulSoup


if __name__ == '__main__':
    args = docopt(__doc__)
    token = args['--token']
    channel = args['--channel']

    response = urllib2.urlopen('http://apod.nasa.gov/apod/astropix.html')
    html = response.read()
    soup = BeautifulSoup(html)
    title = soup.b.string
    img_url = 'http://apod.nasa.gov/%s' % str(soup.img['src'])
    text = re.findall('Explanation:(.*?)Tomorrow', soup.get_text(), re.DOTALL | re.MULTILINE)[0]
    text = text.replace('\n', ' ').rstrip().lstrip()
    text = re.sub("\s\s+", " ", text)  # removes double spaces

    attachments = json.dumps([{
                                  'title': title,
                                  'text': text,
                                  'image_url': img_url,
                                  'title_link': 'http://apod.nasa.gov/apod/astropix.html',
                                  'author_name': '@apod',
                                  'author_link': 'https://twitter.com/apod',
                                  'author_icon': 'https://pbs.twimg.com/profile_images/19829782/apod_normal.png'
                              }])

    # Slack client (using the 'Slacker' library)
    slack = Slacker(token)
    slack.chat.post_message(channel,
                            'Astronomy Picture of the Day - ' + datetime.datetime.now().strftime("%a %B %d, %Y"),
                            username='SpaceBot',
                            icon_url='http://i.imgur.com/xm4a5PP.jpg',
                            attachments=attachments)
