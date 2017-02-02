import sys
import json
import requests
import requests_cache

SEARCH_KEYWORD = sys.argv[1]
API_KEY = sys.argv[2]

items = []


def main():
    requests_cache.install_cache(
        'stations_cache',
        backend='sqlite',
        expire_after=1296000
    )

    search_results = get_search_result()

    for search_result in search_results:
        station_id = search_result['uid']

        aqi_result = get_aqi_info(station_id)

        aqi_index = aqi_result[0]
        aqi_description = get_aqi_description(aqi_index)

        station_name = search_result['station']['name']

        update_time = aqi_result[1]
        timezone = aqi_result[2]
        url = aqi_result[3]

        #To-DO: UnicodeEncodeError station_name
        # title = "[{0}] {1}".format(str(aqi_index), station_name)

        title = str(aqi_index) + " @ " + station_name
        subtitle = "{0}, {1} GMT {2}"\
            .format(aqi_description, update_time, timezone)

        icon = {"type": "png", "path": "aqi_index_scale_color/"\
            + aqi_description + ".png"}

        add_item(title, subtitle, icon, url)

    alfred_item_string = {"items": items}
    print(json.dumps(alfred_item_string))


def get_search_result():
    url_format = 'https://api.waqi.info/search/?token={0}&keyword={1}'
    url = url_format.format(API_KEY, SEARCH_KEYWORD)
    response = requests.get(url)
    data = response.json()['data']

    if response.json()['status'] == 'ok':
        if data != []:
            return data
        else:
            print(json.dumps({"items": [{"title": "Error", "subtitle": "No matching station found"}]}))
    else:
        print(json.dumps({"items": [{"title": "Error", "subtitle": data}]}))


def get_aqi_info(station_id):
    url_format = 'https://api.waqi.info/feed/@{0}/?token={1}'
    url = url_format.format(station_id, API_KEY)
    with requests_cache.disabled():
        response = requests.get(url)

    if response.json()['status'] == 'ok':
        data = response.json()['data']
        aqi_index = data['aqi']

        if aqi_index != '-':
            update_time = data['time']['s']
            timezone = data['time']['tz']
            url = data['city']['url']
            aqi_result = [aqi_index, update_time, timezone, url]
        else:
            aqi_result = [0, "-", "-", ""]
    else:
        aqi_result = [0, "-", "-", ""]

    return aqi_result

def get_aqi_description(aqi_index):
    if aqi_index < 51:
        return 'Good'
    elif aqi_index < 101 and aqi_index > 50:
        return 'Moderate'
    elif aqi_index < 151 and aqi_index > 100:
        return 'Unhealthy For Sensitive Group'
    elif aqi_index < 201 and aqi_index > 150:
        return 'Unhealthy'
    elif aqi_index < 251 and aqi_index > 200:
        return 'Very Unhealthy'
    elif aqi_index < 300 and aqi_index > 250:
        return 'Hazardous'


def add_item(title, subtitle, icon, url):
    item = {
        "title": title,
        "subtitle": subtitle,
        "icon": icon,
        "quicklookurl": url,
        "valid": True,
        "arg": url
    }
    items.append(item)
    return item


if __name__ == '__main__':
    main()
