import requests
import json
import os,dot


def duration(assetid):
	url = os.getenv('SCREENLY_ASSETS_API')
	r = requests.get(url)
	data = r.json()
	r = [i['duration'] for i in data if assetid == i['asset_id']][0]
	return int(r)

if __name__ == '__main__':
    print(duration('8f3a588012024ca1a11c01a062417d74'))