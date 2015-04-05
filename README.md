Slack Space Bot

A Slack bot that posts cool stuff about space. Right now it only does [APOD](http://apod.nasa.gov/apod/astropix.html). 
Maybe it will do more in the future.

# Installation

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

# Usage

SpaceBot is a typical command line program. Once installed, you will have the command `spacebot` available for use. 

To have `SpaceBot` run every day at 12:00pm, and post to the chat with channel (or group) ID `CHANNEL` (this ID can be 
retrieved from the Slack REST API), using the Slack API token `TOKEN`, do:
 
    $ spacebot -c CHANNEL -t TOKEN

Other parameters such as the time of day, logging level, and log file can be set at runtime as well. By default, 
SpaceBot will log all program output to stderr. Consider specifying a log file.

Refer to the full usage documentation for more details (or just look at `spacebot.py`):

    $ spacebot --help.
   
Once you have SpaceBot running in a terminal, just leave it running until you want to stop it with CTRL+C or `kill` or
whatever your method of choice is. Alternatively you can run it in the background:

    $ spacebot [OPTIONS] &

That's about it for now :)

# Development

Start a [virtual environment](https://virtualenv.pypa.io/en/latest/): 

    $ virtualenv venv

Install the requirements:

    $ pip install -r requirements.txt
