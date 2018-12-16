#!/usr/bin/python
import requests
from bs4 import BeautifulSoup
import json
import argparse

base_url = "https://eservice.energieag.at"

def parse(html):
    return BeautifulSoup(html, features="html.parser")

def login(session, user, password):
    session.get(base_url + '/eServiceWeb/main.html')
    dashboard = session.post(base_url + '/eServiceWeb/j_security_check', {'j_username': user, 'j_password': password})
    if dashboard.status_code != 200:
        print("Error, status war nicht 200")
        return None
    else:
        return parse(dashboard.text)

def energiemanager(session, dashboard):
    emlink = dashboard.find("a", string="Energiemanager")['href']
    em = session.get(base_url + emlink)
    if em.status_code != 200:
        print("Error, em not open")
        return None
    else:
        return parse(em.text)

def extractParams(energiemanager):
    overviewForm = energiemanager.find(id="overview")
    def valById(myid):
        return overviewForm.find(id=myid)['value']
    session_token = overviewForm.find(attrs={"name": "session_token"})['value']
    pod = overviewForm.find(id="overview_manager_pods").find("option", attrs={"selected": "selected"})['value']
    return {'session_token': session_token,
            'accountId': valById("overview_accountId"),
            'contractId': valById("overview_contractId"),
            'manager.year': valById("overview_manager_year"),
            'manager.month': valById("overview_manager_month"),
            'manager.day': valById("overview_manager_day"),
            'manager.pods': pod,
            'manager.comparePod': ''}

def getActiveJson(session, energiemanager):
    activeParams = extractParams(energiemanager)
    activeHref = energiemanager.find(id="activePower")['data-target']
    postResult = session.post(base_url + activeHref, activeParams)
    if postResult.status_code != 200:
        return print("error posting active"), None
    else:
        return (json.loads(postResult.text), activeParams['manager.pods'])

def extractTotalKwh(activeJson, pod):
    def infoValueByName(infotexts, name):
        for infotext in infotexts:
            if 'description' in infotext and infotext['description'] == name:
                return infotext['value']
        return None
    verbrauchstr = infoValueByName(activeJson['data'][pod][0]['infobox'], "Verbrauch:")
    vorkomma, nachkomma = verbrauchstr.split(' ')[0].split(',')
    return vorkomma + "." + nachkomma

def parseCmdLine():
    parser = argparse.ArgumentParser(description='Stromverbrauch auslesen.')
    parser.add_argument('--user', help='the user to login to the webinterface', required=True)
    parser.add_argument('--password', help='the password', required=True)

    return parser.parse_args()

s = requests.session()

args = parseCmdLine()
dashboardHtml = login(s, args.user, args.password)
energiemanagerHtml = energiemanager(s, dashboardHtml)
activeJson, pod = getActiveJson(s, energiemanagerHtml)
verbrauch = extractTotalKwh(activeJson, pod)
print(verbrauch)