#!/usr/bin/python
#   Copyright 2013 Pete Burgers
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import urllib2
import urlparse
from flask import *

MAX_FEED_SIZE = 10*1024*1024
MAX_FEED_ITEMS = 1000
MIN_REPLACE_SIZE = 10

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/mobilator")
def mobilator():
    feed_url = normalise_url(request.args["feed_url"])
    normal_site = normalise_url(request.args["normal_site"])
    mobile_site = normalise_url(request.args["mobile_site"])

    if normal_site == "http://":
        normal_site = urlparse.urljoin(feed_url, "/")

    f = urllib2.urlopen(feed_url)
    content = f.read(MAX_FEED_SIZE)
    if len(content) == MAX_FEED_SIZE:
        return "Error: Feed is too long to process"
    if len(normal_site) < MIN_REPLACE_SIZE or len(mobile_site) < MIN_REPLACE_SIZE:
        return "Error: Search/replace website URLs must be at least %s characters" % MIN_REPLACE_SIZE

    encoding = f.info().gettype()
    try:
        content = unicode(content, encoding)
    except LookupError:
        content = unicode(content, "utf-8")

    content = content.replace(normal_site, mobile_site, MAX_FEED_ITEMS)
    return content

def normalise_url(url):
    if urlparse.urlsplit(url).scheme == "":
        url = "http://" + url
    if urlparse.urlsplit(url).path == "":
        url = url + "/"
    if url.endswith("///"):
        url = url[:-1]
    return url


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", "-d", action="store_true")
    args = parser.parse_args()

    app.run(debug=args.debug)
