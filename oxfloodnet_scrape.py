#!/usr/bin/python
import requests
import datetime
import eeml
from lxml.html.soupparser import fromstring
from lxml.etree import tostring
from time import sleep

# Ancient code running as a cron job on badgermedia server, scraping Environment Agency feeds for a few sensors in Oxford
# and updating a legacy Xively feed.
# I HAVE NO IDEA WHAT I'M DOING
#
# Original code from russss https://github.com/crouchingbadger/ea_scrape

# area_id -> [station_id]
SOURCES = [[136495, 7074, '88571'], # Seacourt Stream at Minns Estate [88571]
           [136495, 7075, '88603'], # Bulstake Stream at New Botley
           [136495, 7057, '88605'], # Thames - Upstream at Osney Lock
           [136495, 7076, '88607'], # Hinksey Stream at Cold Harbour
           [136497, 7071, '88610'], # Cherwell - Upstream at Kings Mill
           [136497, 7072, '88611'], # Thames - Upstream at Iffley Lock
           [136497, '7072&Sensor=D', '88615'], # Thames - Downstream at Iffley Lock
                ]


FEED = '#FEEDID'
API_KEY = '#APIKEY' 
API_URL = '/v2/feeds/{feednum}.xml' .format(feednum = FEED)


def get_data(area_id, station_id):
    url = 'http://www.environment-agency.gov.uk/homeandleisure/floods/riverlevels/%s.aspx?stationId=%s'
    try:
        r = requests.get(url % (area_id, station_id))
#       print vars(r)

        data = fromstring(r.content)

        date_text = data.find('.//div[@id="content"]/div/div/p').text

        time, date = date_text.strip('Last updated ').split(' on ')

        day, month, year = map(int, date.split('/'))
        hour, minute = map(int, time.split(':'))

        height = float(data.find(".//div[@id='station-detail-left']//div[@class='plain_text']/p"
                                                                ).text.split(' is ')[1].split(' ')[0])

        return datetime.datetime(year, month, day, hour, minute), height
    except Exception:
        print "couldn't scrape"
        pass


for stationinfo in SOURCES:
        print stationinfo

        area_id = stationinfo[0]
        station_id = stationinfo[1]
        station_feed = stationinfo[2]

        try:
                readdate, level = get_data(area_id, station_id)
                print "Returned:", readdate, level
                api_url = "/v2/feeds/"+ station_feed + ".xml"

                print api_url
                try:
                        # Open up Xively feed
                        pac = eeml.Pachube(api_url, API_KEY)

                        # Update feed
                        pac.update([eeml.Data("Level", level, unit=eeml.Unit("Metre",'basicSI',"m") )])

                        try:
                                pac.put()

                        except:
                                print "couldn't connect to xively"
                                print "Xively error:", sys.exc_info()[0]
                                pass
                except:
                        print "problem creating url"
                        pass
        except Exception:
                print "Feed unavailable"

        sleep(2)

