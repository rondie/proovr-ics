import json
import uuid

from html.parser import HTMLParser
from collections import defaultdict
from ics import Calendar, Event


import requests



headers = {"Accept": "application/json, text/plain, */*", "Application-Agent": "Proovr"}

def mailConfCode(email):
    state = uuid.uuid5(uuid.NAMESPACE_URL, email)
    data = {'Email': email, 'State': str(state)}
    requests.post('https://api.proovr.com/v0.1/credentials/email/request', json=data)

def getBookedData(email, bearer):
    headers["Authorization"] = "Bearer " + bearer
    bookingPage = requests.get('https://registration.proxyclick.com/api/app/CO-DHD956/em/bookable-days', headers=headers)
    bookingData = json.loads(bookingPage.text)
    bookedData = [i for i in bookingData if (i['booking'])]
    return(bookedData)

def makeIcs(bookedData):
    cal = Calendar()
    for entry in bookedData:
        event = Event()
        event.begin = entry['date']
        event.make_all_day()
        event.name = entry['booking']['company']['name']
        event.description = "Lunch=" + str(entry['booking']['customFields'][0]['value'])
        event.location = entry['booking']['deskArea']['name']
        event.geo = entry['booking']['company']['latitude'],entry['booking']['company']['longitude']
        event.url = 'https://web.proovr.com/'
        cal.events.add(event)
    cal_bytes = bytes(str(cal), 'utf-8')
    return cal_bytes
