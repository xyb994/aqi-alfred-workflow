import sys
import json
import requests
import requests_cache

API_KEY = sys.argv[1]

items = []

def get_aqi_by_ip():
    url_format = 'https://api.waqi.info/feed/here/?token={0}'
    url = url_format.format(API_KEY)

    with requests_cache.disabled():
        response = requests.get(url)

    if response.json()['status'] == 'ok':
        data = response.json()['data']

        aqi_index = data['aqi']
        update_time = data['time']['s']
        timezone = data['time']['tz']
        url = data['city']['url']
        city_name = data['city']['name']

        if aqi_index != '-':
            aqi_result = [aqi_index, update_time, timezone, url, city_name]
        else:
            aqi_result = [0, update_time, timezone, url, city_name]
        return aqi_result
    else:
        print(json.dumps({"items": [{"title": "Error", "subtitle": data}]}))

def main():
    requests_cache.install_cache(
        'stations_cache',
        backend='sqlite',
        expire_after=1296000
    )

    aqi_result = get_aqi_by_ip()

    aqi_index = aqi_result[0]
    aqi_description = get_aqi_description(aqi_index)

    update_time = aqi_result[1]
    timezone = aqi_result[2]
    url = aqi_result[3]
    city_name = aqi_result[4]

    #To-DO: UnicodeEncodeError station_name
    # title = "[{0}] {1}".format(str(aqi_index), station_name)

    title = str(aqi_index) + " @ " + city_name

    subtitle = "{0}, {1} GMT{2}"\
        .format(aqi_description, update_time, timezone)

    icon = {"type": "png", "path": "aqi_index_scale_color/"\
        + aqi_description + ".png"}

    add_item(title, subtitle, icon, url)

    alfred_item_string = {"items": items}
    print(json.dumps(alfred_item_string))


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
        "uid": 'aqi',
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
