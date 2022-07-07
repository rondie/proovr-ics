import json
import re
import urllib.parse
import uuid
from io import BytesIO

from app.actions import getBookedData, mailConfCode, makeIcs

from flask import Flask, redirect, render_template, request, send_file

import requests

app = Flask(__name__)


headers = {"Accept": "application/json, text/plain, */*", "Application-Agent": "Proovr"}


@app.route('/', methods=["GET", "POST"])
def getemail():
    if request.method == "GET":
        return render_template("page.html")
    if request.method == "POST":
        email = request.form['E-mail address']
        emailurl = urllib.parse.quote(email.encode("utf8"))
        return redirect(emailurl)


@app.route('/<emailurl>', methods=["GET", "POST"])
def getconfcode(emailurl):
    if request.method == "GET":
        email = urllib.parse.unquote(emailurl)
        emailurl = urllib.parse.quote(email.encode("utf8"))
        return render_template("page.html", email=email, emailurl=emailurl)
    if request.method == "POST":
        confcode = request.form['E-mail Confirmation Code']
        email = urllib.parse.unquote(emailurl)
        emailurl = urllib.parse.quote(email.encode("utf8"))
        if confcode:
            state = uuid.uuid5(uuid.NAMESPACE_URL, email)
            emailCredentialData = {"Email": email, "State": str(state), "Token": confcode}
            emailCredentialPage = requests.post('https://api.proovr.com/v0.1/credentials/email/verify', json=emailCredentialData)
            if emailCredentialPage.status_code != 200:
                return render_template("page.html", email=email, emailurl=emailurl, error=emailCredentialPage.json())
            else:
                emailCredentialPageJson = json.loads(emailCredentialPage.text)
                emailCredential = emailCredentialPageJson['emailCredential']
                getBearerData = {"Credentials": {"Email": emailCredential}}
                getBearerPage = requests.post('https://proovr.proxyclick.com/employee/view-booking', headers=headers, json=getBearerData)
                redirectUrlJson = json.loads(getBearerPage.text)
                redirectUrlMatch = re.search('jwt=([a-z].*)&', str(redirectUrlJson))
                bearer = redirectUrlMatch.group(1)
                return redirect(emailurl + '/' + bearer)
        else:
            mailConfCode(email)
            return render_template("page.html", email=email, emailurl=emailurl)


@app.route('/<emailurl>/<bearer>')
def icsPage(emailurl, bearer):
    email = urllib.parse.unquote(emailurl)
    bookedData = getBookedData(email, bearer)
    return render_template("page.html", email=email, emailurl=emailurl, bearer=bearer, bookedData=bookedData)


@app.route('/<emailurl>/<bearer>/proovr.ics')
def ics(emailurl, bearer):
    email = urllib.parse.unquote(emailurl)
    bookedData = getBookedData(email, bearer)
    file = BytesIO(makeIcs(bookedData))
    return send_file(
        file,
        attachment_filename='proovr.ics',
        as_attachment=True)
    file.close
