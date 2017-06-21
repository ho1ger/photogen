#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from os import listdir
from os.path import isfile, join
from fractions import Fraction
from urllib.request import urlopen
from xml.dom.minidom import parse, parseString
import exifread # pip install exifread
import geopy # pip install geopy

# Helper function to convert the GPS coordinates stored in the EXIF to degrees in float format

def __convert_to_degress(value):
    d = float(Fraction(str(value.values[0])))
    m = float(Fraction(str(value.values[1])))
    s = float(Fraction(str(value.values[2])))
    return d + (m / 60.0) + (s / 3600.0)

# does some minidom black magic I do not fully understand
# copied from: https://docs.python.org/2/library/xml.dom.minidom.html
def __getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

# Helper function that retrievs info from wikipedia to one x / y coordinate
def __retrieveInfo(x, y, user, lang = "de"):
    url = "http://api.geonames.org/findNearbyWikipedia?lat={0}&lng={1}&username={2}&lang={3}".format(x, y, user, lang)
    response = urlopen(url)
    xml = response.read()
    # parse xml
    dom = parseString(xml)
    # go through the dom object, filter out interesting parts.
    # still ugly, needs to be rewritten
    results = []
    doParse = True
    i = 0
    while doParse:
        try:
            titledom = dom.getElementsByTagName("title")[i]
            title = __getText(titledom.childNodes)
            summarydom = dom.getElementsByTagName("summary")[i]
            summary = __getText(summarydom.childNodes)
            wikipediaUrldom = dom.getElementsByTagName("wikipediaUrl")[i]
            wikipediaUrl = __getText(wikipediaUrldom.childNodes)
            results.append((title, summary, wikipediaUrl))
            i += 1
        except:
            doParse = False
    return results

# ----------

if len(sys.argv) != 2:
    print("Wrong amount of arguments. Expected: photogen.py /path/to/folder")
else:
    path = sys.argv[1]

user = "drscheme"
weburl = "photos"
x = path.find("/")
webpath = path[x+1:]
photos = [f for f in listdir(path) if isfile(join(path, f))]

for photo in photos:
    if (("jpeg" in photo) or ("jpg" in photo) or ("JPEG" in photo) or ("JPG" in photo)):

        line = "![](/" + join(weburl, webpath, photo) + ")<br/>"
        print(line)

        try:
            photofile = open(join(path, photo), 'rb')
            tags = exifread.process_file(photofile)
            photofile.close()

            xns = str(tags["GPS GPSLatitudeRef"])
            x = tags["GPS GPSLatitude"]
            xdeg = __convert_to_degress(x)
            if xns == ("S"):
                xdeg = xdeg * (-1.0)

            ywe = str(tags["GPS GPSLongitudeRef"])
            y = tags["GPS GPSLongitude"]
            ydeg = __convert_to_degress(y)
            if ywe == ("W"):
                ydeg = ydeg * (-1.0)

            mapsurl = "https://www.google.de/maps/place/{0},{1}".format(xdeg, ydeg)
            urls = "[Picture location]({0}) -- ".format(mapsurl)
            urls += "Wiki-Links: "
            results = __retrieveInfo(xdeg, ydeg, user)
            for result in results:
                urls += "[{0}]({1}) • ".format(result[0], result[2])
            print(urls[0:-3])
            print("\n")

        except:
            pass
