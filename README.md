# Slack Space Bot
[![Build Status](https://travis-ci.org/ccampo133/slack-spacebot.svg?branch=master)](https://travis-ci.org/ccampo133/slack-spacebot)

A python Slack bot that posts cool stuff about space. Right now it only does [APOD](http://apod.nasa.gov/apod/astropix.html). 
Maybe it will do more in the future (hopefully!).

SpaceBot is built and tested on Python 2.6, 2.7, 3.2, 3.3, 3.4, and the current nightly Python build.

## Installation

To install the latest build from `master`, you can install using `pip`:

    $ pip install git+git://github.com/ccampo133/slack-spacebot.git
    
Alternatively, to install from source:

    $ python setup.py install
    
To uninstall using `pip`:

    $ pip uninstall slack-spacebot
    
Alternatively, you can uninstall the old fashioned way using `setup.py`. To record list of installed files, use:
    
    $ python setup.py install --record files.txt

Then use xargs to do the removal of the install files listed in `files.txt`:
    
    cat files.txt | xargs rm -rf
    
Really though, just use `pip`.

## Usage

SpaceBot is a typical command line program. Once installed, you will have the command `spacebot` available for use in
your terminal.

To have SpaceBot run immediately, and post to the chat with channel (or private group) ID `CHANNEL` (this ID can be 
retrieved from the [Slack REST API](https://api.slack.com/web)), using the Slack API token `TOKEN`, and your 
data.nasa.gov API key `KEY` (apply for an API key at https://data.nasa.gov/developer/external/planetary/#apply-for-an-api-key), 
do:
 
    $ spacebot -c CHANNEL -t TOKEN -k KEY

Note that while the `-k` flag is technically optional (it will default to `DEMO_KEY`), it is unknown if this will 
continue to be supported by the data.nasa.gov folks themselves.

Additionally, you can have SpaceBot run on a schedule, once per day, at your specified time. The time of day should be
in 24 hour `HH:mm` format, e.g. 13:00 for 1 PM. To specify the time of day SpaceBot runs, use the `-T --time` option:

    $ spacebot -c CHANNEL -t TOKEN -T 13:00

The recommended approach to running SpaceBot, however, is to use `cron` or a similar scheduler. The example `crontab`
line runs SpaceBot every day at 11:00 AM:

    0 11 * * * spacebot -c CHANNEL -t TOKEN

Other parameters such as the logging level, log file, and APOD picture data can be set at runtime as well. By default, 
SpaceBot will log all program output to stderr. Consider specifying a log file. Refer to the full usage documentation 
for more details (or just look at `spacebot.py`):

    $ spacebot --help.
   
If you have SpaceBot running in a terminal (i.e. scheduled), just leave it running until you want to stop it with CTRL+C 
or `kill` or whatever your method of choice is. Alternatively you can just run it in the background:

    $ spacebot [OPTIONS] &

That's about it for now :)

## Development

Start a [virtual environment](https://virtualenv.pypa.io/en/latest/): 

    $ virtualenv venv
    $ source venv/bin/activate  # Note: Bash users may have to use . if source is not available

Install the requirements:

    $ pip install -r requirements.txt

You can change SpaceBot's Slack name, Slack icon, and other APOD parameters at the head of `spacebot.py`.

## Screenshots

![](/../screenshots/slack1.png?raw=true)
