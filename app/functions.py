import json
import re
import uuid

from ics import Calendar, Event


import requests


registrationsite = 'https://registration.proxyclick.com'
apisite = 'https://api.proovr.com'
proovrsite = 'https://proovr.proxyclick.com'
website = 'https://web.proovr.com'
bhid = "CO-DHD956"
headers = {
        "Accept": "application/json, text/plain, */*",
        "Application-Agent": "Proovr"
        }


def mailConfCode(email):
    state = uuid.uuid5(uuid.NAMESPACE_URL, email)
    data = {'Email': email, 'State': str(state)}
    requests.post(
            apisite + '/v0.1/credentials/email/request',
            json=data
            )


def getJwt(emailCredential):
    getJwtData = {"Credentials": {"Email": emailCredential}}
    getJwtPage = requests.post(
        proovrsite + '/employee/view-booking',
        headers=headers,
        json=getJwtData
        )
    redirectUrlJson = json.loads(getJwtPage.text)
    redirectUrlMatch = re.search(
        'jwt=([a-z].*)&',
        str(redirectUrlJson)
        )
    jwt = redirectUrlMatch.group(1)
    return getJwtPage.status_code, getJwtPage.text, jwt


def getBookedData(jwt):
    headers["Authorization"] = "Bearer " + jwt
    bookingPage = requests.get(
        registrationsite + '/api/app/' + bhid + '/em/bookable-days',
        headers=headers
        )
    bookingData = json.loads(bookingPage.text)
    return (bookingData)


def makeIcs(bookedData):
    cal = Calendar()
    for entry in bookedData:
        event = Event()
        event.begin = entry['date']
        event.make_all_day()
        event.name = entry['booking']['company']['name']
        event.description = \
            "Lunch=" + str(entry['booking']['customFields'][0]['value'])
        event.location = entry['booking']['deskArea']['name'] + ' - Desk ' + str(entry['booking']['deskArea']['deskNumber'])
        event.geo = \
            entry['booking']['company']['latitude'], \
            entry['booking']['company']['longitude']
        event.url = website
        cal.events.add(event)
    cal_bytes = bytes(str(cal), 'utf-8')
    return cal_bytes


def seatsavailable(jwt):
    headers["Authorization"] = "Bearer " + jwt
    seatsavailablePage = requests.get(
        registrationsite + '/api/app/' + bhid + '/em/bookable-days',
        headers=headers
        )
    seatsavailable = json.loads(seatsavailablePage.text)
    seatsAvailable = [
        {"date": entry["date"], "seatsAvailable": entry["seatsAvailable"]}
        for entry in seatsavailable
    ]
    return (seatsAvailable)
