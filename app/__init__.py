import json
import urllib.parse
import uuid
from io import BytesIO

from app.functions import getBookedData, mailConfCode, makeIcs, getJwt, seatsavailable

from flask import Flask, redirect, render_template, request, send_file

import requests

app = Flask(__name__)


headers = {
        "Accept": "application/json, text/plain, */*",
        "Application-Agent": "Proovr"
        }


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
        emailurl = \
            urllib.parse.quote(email.encode("utf8"))
        if confcode:
            state = uuid.uuid5(uuid.NAMESPACE_URL, email)
            emailCredentialData = {
                "Email": email,
                "State": str(state),
                "Token": confcode
                }
            emailCredentialPage = requests.post(
                'https://api.proovr.com/v0.1/credentials/email/verify',
                json=emailCredentialData
                )
            if emailCredentialPage.status_code != 200:
                return render_template(
                    "page.html",
                    email=email,
                    emailurl=emailurl,
                    error=emailCredentialPage.json()
                    )
            else:
                emailCredentialPageJson = json.loads(emailCredentialPage.text)
                emailCredential = emailCredentialPageJson['emailCredential']
                status_code, error, jwt = getJwt(emailCredential)
                if status_code == 200:
                    return redirect(
                        emailurl + '/' + emailCredential
                        )
                else:
                    return render_template(
                        "page.html",
                        email=email,
                        emailurl=emailurl,
                        error=error
                        )
        else:
            mailConfCode(email)
            return render_template(
                "page.html",
                email=email,
                emailurl=emailurl)


@app.route('/<emailurl>/<emailCredential>')
def icsPage(emailurl, emailCredential):
    email = urllib.parse.unquote(emailurl)
    status_code, error, jwt = getJwt(emailCredential)
    if status_code == 200:
        bookingData = getBookedData(jwt)
        return render_template(
            "page.html",
            email=email,
            emailurl=emailurl,
            emailCredential=emailCredential,
            bookingData=bookingData
            )
    else:
        return render_template(
            "page.html",
            email=email,
            emailurl=emailurl,
            error=error
            )


@app.route('/<emailurl>/<emailCredential>/proovr.ics')
def ics(emailurl, emailCredential):
    email = urllib.parse.unquote(emailurl)
    status_code, error, jwt = getJwt(emailCredential)
    if status_code == 200:
        bookingData = getBookedData(jwt)
        bookedData = [i for i in bookingData if (i['booking'])]
        file = BytesIO(makeIcs(bookedData))
        return send_file(
            file,
            download_name='proovr.ics',
            as_attachment=True)
        file.close
    else:
        return render_template(
            "page.html",
            email=email,
            emailurl=emailurl,
            error=error
            ), 500

@app.route('/<emailurl>/<emailCredential>/metrics')
def metrics(emailurl, emailCredential):
    email = urllib.parse.unquote(emailurl)
    status_code, error, jwt = getJwt(emailCredential)
    if status_code == 200:
        seatsAvailable = seatsavailable(jwt)
        return seatsAvailable
    else:
        return render_template(
            "page.html",
            email=email,
            emailurl=emailurl,
            error=error
            ), 500