import json
import re
import uuid

from datetime import date
from icalendar import Calendar, Event


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
    cal.add('prodid', '-//proovr-ics//EN')
    cal.add('version', '2.0')
    for entry in bookedData:
        event = Event()
        event.add('dtstart', date.fromisoformat(entry['date']))
        event.add('summary', entry['booking']['company']['name'])
        event.add('description',
                  "Lunch=" + str(entry['booking']['customFields'][0]['value']))
        event.add('location',
                  entry['booking']['deskArea']['name'] +
                  ' - Desk ' +
                  str(entry['booking']['deskArea']['deskNumber']))
        event.add('geo', (entry['booking']['company']['latitude'],
                          entry['booking']['company']['longitude']))
        event.add('url', website)
        cal.add_component(event)
    return cal.to_ical()


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
