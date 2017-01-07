import requests
import datetime
from lxml import html

from pymongo import MongoClient


# configure the database
client = MongoClient()
db = client.fantasy
data = db.players_2

USERNAME = "xxxxxx"
PASSWORD = "xxxxxx"

LOGIN_URL = "http://fantasychallenge.euroleague.net/"
URL_TEMPLATE = "http://fantasychallenge.euroleague.net/playermarket.php?id_pos={pos}"


def main():
    session_requests = requests.session()

    # Get login CMD token
    result = session_requests.get(LOGIN_URL)
    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='CMD']/@value")))[0]

    # Create payload
    payload = {
        "usuario": USERNAME, 
        "clave": PASSWORD, 
        "CMD": authenticity_token
    }

    # Perform login
    result = session_requests.post(LOGIN_URL, data = payload, headers = dict(referer = LOGIN_URL))


    # for each page
    for pos in range(1, 4):
        URL = URL_TEMPLATE.format(pos=pos)
        print URL

        # Scrape url
        result = session_requests.get(URL, headers = dict(referer = URL))
        tree = html.fromstring(result.content)


        bucket_names        = tree.xpath('//div[@id="players_1"]/ul/li/a/text()')
        bucket_teams        = tree.xpath('//div[@id="players_1"]/ul/li[3]/text()')
        bucket_balance      = tree.xpath('//div[@id="players_1"]/ul/li[4]/text()')
        bucket_points_avg   = tree.xpath('//div[@id="players_1"]/ul/li[5]/text()')
        bucket_price        = tree.xpath('//div[@id="players_1"]/ul/li[6]/text()')
        bucket_grow_15      = tree.xpath('//div[@id="players_1"]/ul/li[7]/text()')
        bucket_keep         = tree.xpath('//div[@id="players_1"]/ul/li[8]/text()')
        bucket_down_15      = tree.xpath('//div[@id="players_1"]/ul/li[9]/text()')
        bucket_next_rival   = tree.xpath('//div[@id="players_1"]/ul/li[10]/text()')

        date = datetime.datetime.utcnow()

        if pos == 1:
           position = "Guard"
        elif pos == 2:
           position = "Forward"
        elif pos == 3:
           position = "Center"

        players_dict        = [{'name':bn,'team':bt, 'balance':bb, 'points_avg':float(bpavg),'price':float(bp), 'grow_15':float(bg), 'keep':float(bk),'down_15':float(bd), 'next_rival':bnext}
            for bn, bt, bb, bpavg, bp, bg, bk, bd, bnext 
                in zip(bucket_names, bucket_teams, bucket_balance, bucket_points_avg, bucket_price, bucket_grow_15, bucket_keep, bucket_down_15, bucket_next_rival)]

        for player in players_dict:
            player["datetime"] = date
            player["position"] = position
            print player

        data.insert(players_dict)


if __name__ == '__main__':
    main()




