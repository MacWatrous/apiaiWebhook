#!/usr/bin/env python

import urllib
import json
import os
import requests
import re

from flask import Flask
from flask import request
from flask import make_response

#Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    #print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    #if req.get("result").get("action") != "yahooWeatherForecast":
        #return {}

    if req.get("result").get("action") == "drugInquiry":
        inquiry = returnInquiry(req)
        speech = inquiry
        return {
            "speech": speech,
            "displayText": speech,
            #"data": data,
            #"contextOut": [],
            "source": "apiai-weather-webhook-sample"
        }

    if req.get("result").get("action") == "drugInteractions":
        inquiry = returnInteractions(req)
        speech = inquiry
        return {
            "speech": speech,
            "displayText": speech,
            #"data": data,
            #"contextOut": [],
            "source": "apiai-weather-webhook-sample"
        }

    if req.get("result").get("action") == "drugInteractionsPrior":
        inquiry = returnInteractionsPrior(req)
        speech = inquiry
        return {
            "speech": speech,
            "displayText": speech,
            #"data": data,
            #"contextOut": [],
            "source": "apiai-weather-webhook-sample"
        }
    if req.get("result").get("action") == "drugRoute":
        inquiry = returnRoute(req)
        speech = inquiry
        return {
            "speech": speech,
            "displayText": speech,
            #"data": data,
            #"contextOut": [],
            "source": "apiai-weather-webhook-sample"
        }
    else: 
        return {}

    #yahoo stuff
    #baseurl = "https://query.yahooapis.com/v1/public/yql?"
    #yql_query = makeYqlQuery(req)
    #if yql_query is None:
    #    return {}
    #yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
    #result = urllib.urlopen(yql_url).read()
    #data = json.loads(result)
    #res = makeWebhookResult(data)
    #return res

#def returnNDC(rxcui):
    #url = "https://rxnav.nlm.nih.gov/REST/ndcproperties.json?id=" + rxcui
    #result = (requests.get(url)).text
    #lhs, rhs = result.split("ndc9\": \"",1)
    #lhs, rhs = rhs.split("\",\"ndc10",1)
    #ndc = lhs
    #return ndc;

#def returnRXCUI(req):
    #baseurl = "https://rxnav.nlm.nih.gov/REST/approximateTerm.json?"
    #result = req.get("result")
    #parameters = result.get("parameters")
    #drug = parameters.get("drug")
    #url = baseurl + "term=" + drug + "&maxEntries=1"
    #result = (requests.get(url)).text
    #lhs, rhs = result.split("rxcui\":\"",1)
    #lhs, rhs = rhs.split("\",\"rxaui",1)
    #rxcui = lhs
    #return rxcui;

def returnInquiry(req):
    baseurl = "https://api.fda.gov/drug/label.json?search=openfda."
    result = req.get("result")
    parameters = result.get("parameters")
    drug = parameters.get("drug")
    url = baseurl + "generic_name:\"" + drug + "\""
    result = requests.get(url)
    if result.status_code != 200:
        url = baseurl + "brand_name:\"" + drug + "\""
        result = (requests.get(url))
        print("help!")
        result = result.text
        lhs, rhs = result.split("indications_and_usage\": [\n        \"",1)
        rhs = rhs.replace('\"',".")
        lhs, rhs = rhs.split(".",1)
        inquiry = lhs
        return inquiry

    result = result.text
    lhs, rhs = result.split("indications_and_usage\": [\n        \"",1)
    rhs = rhs.replace('\"',".")
    lhs, rhs = rhs.split(".",1)
    inquiry = lhs
    return inquiry

def returnRoute(req):
    baseurl = "https://api.fda.gov/drug/label.json?search="
    result = req.get("result")
    parameters = result.get("parameters")
    drug = parameters.get("drug")
    url = baseurl + drug + "&count=openfda.route.exact"
    result = requests.get(url)

    result = result.text
    lhs, rhs = result.split("term\": \"",1)
    lhs, rhs = rhs.split("\"",1)
    inquiry = lhs
    inquiry = inquiry.lower()
    return "The most common route of administration we've found for " + drug + " is " + inquiry + "."


def returnInteractions(req):
    baseurl = "https://api.fda.gov/drug/label.json?search=openfda."
    result = req.get("result")
    parameters = result.get("parameters")
    drug = parameters.get("drug")

    url = baseurl + "generic_name:\"" + drug + "\""
    result = requests.get(url)
    if result.status_code != 200:
        url = baseurl + "brand_name:\"" + drug + "\""
        result = (requests.get(url))
        print("help!")
    result = result.text
    lhs, rhs = result.split("rxcui",1)
    rhs = rhs[16:]
    array = re.findall(r"\w+",rhs)
    rxcui = array[0]

    if "true" == parameters.get("alcohol", "true"):
        drug2 = parameters.get("drug1")
        url2 = baseurl + "generic_name:\"" + drug2 + "\""
        result2 = requests.get(url2)
        if result2.status_code != 200:
            url2 = baseurl + "brand_name:\"" + drug2 + "\""
            result2 = (requests.get(url2))
            print("help!2")
        result2 = result2.text
        lhs, rhs = result2.split("rxcui",1)
        rhs = rhs[16:]
        array = re.findall(r"\w+",rhs)
        rxcui2 = array[0]
    else:
        rxcui2 = "448"
        print("there's alcohol here")

    baseurl2 = "https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis="
    url3 = baseurl2 + rxcui + "+" + rxcui2
    result3v2 = requests.get(url3)
    result3 = result3v2.text

    if "severity" in result3:
        if rxcui2 == "448":
            drug2 = "alcohol"
            temp = drug
            drug = drug2
            drug2 = temp

        lhs, rhs = result3.split("description\":\"",1)
        lhs, rhs = rhs.split("\"",1)
        interaction = lhs
        print(result3v2.json())
        result3v2 = result3v2.json()
        resultDrug = result3v2['fullInteractionTypeGroup'][0]['fullInteractionType'][0]['interactionPair'][0]['interactionConcept'][0]['minConceptItem']['name']
        resultDrug2 = result3v2['fullInteractionTypeGroup'][0]['fullInteractionType'][0]['interactionPair'][0]['interactionConcept'][1]['minConceptItem']['name']
        print(resultDrug)
        print(resultDrug2)

        index = (interaction.lower()).find(resultDrug.lower())
        drug = drug.lower()
        drug = drug[0].upper() + drug[1:]
        interaction = interaction[:index] + drug + " (" + interaction[index:]
        index = index + len(resultDrug) + len(drug) + 2
        interaction = interaction[:index] + ")" + interaction[index:]

        index = (interaction.lower()).find(resultDrug2.lower())
        interaction = interaction[:index] + drug2.lower() + " (" + interaction[index:]
        index = index + len(resultDrug2) + len(drug2) + 2
        interaction = interaction[:index] + ")" + interaction[index:]
        
        return interaction
    return "There is no interaction between these drugs!"

def returnInteractionsPrior(req):
    baseurl = "https://api.fda.gov/drug/label.json?search=openfda."
    result = req.get("result")
    parameters = result.get("parameters")
    drug = parameters.get("drug")

    url = baseurl + "generic_name:\"" + drug + "\""
    result = requests.get(url)
    if result.status_code != 200:
        url = baseurl + "brand_name:\"" + drug + "\""
        result = (requests.get(url))
        print("help!")
    result = result.text
    lhs, rhs = result.split("rxcui",1)
    rhs = rhs[16:]
    array = re.findall(r"\w+",rhs)
    rxcui = array[0]

    if "true" == parameters.get("alcohol", "true"):
        drug2 = parameters.get("drug1")
        url2 = baseurl + "generic_name:\"" + drug2 + "\""
        result2 = requests.get(url2)
        if result2.status_code != 200:
            url2 = baseurl + "brand_name:\"" + drug2 + "\""
            result2 = (requests.get(url2))
            print("help!2")
        result2 = result2.text
        lhs, rhs = result2.split("rxcui",1)
        rhs = rhs[16:]
        array = re.findall(r"\w+",rhs)
        rxcui2 = array[0]
    
    else:
        rxcui2 = "448"

    baseurl2 = "https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis="
    url3 = baseurl2 + rxcui + "+" + rxcui2
    result3v2 = requests.get(url3)
    result3 = result3v2.text

    if "severity" in result3:
        if rxcui2 == "448":
            drug2 = "alcohol"
            temp = drug
            drug = drug2
            drug2 = temp

        lhs, rhs = result3.split("description\":\"",1)
        lhs, rhs = rhs.split("\"",1)
        interaction = lhs
        print(result3v2.json())
        result3v2 = result3v2.json()
        resultDrug = result3v2['fullInteractionTypeGroup'][0]['fullInteractionType'][0]['interactionPair'][0]['interactionConcept'][0]['minConceptItem']['name']
        resultDrug2 = result3v2['fullInteractionTypeGroup'][0]['fullInteractionType'][0]['interactionPair'][0]['interactionConcept'][1]['minConceptItem']['name']
        print(resultDrug)
        print(resultDrug2)

        index = (interaction.lower()).find(resultDrug.lower())
        drug = drug.lower()
        drug = drug[0].upper() + drug[1:]
        interaction = interaction[:index] + drug + " (" + interaction[index:]
        index = index + len(resultDrug) + len(drug) + 2
        interaction = interaction[:index] + ")" + interaction[index:]

        index = (interaction.lower()).find(resultDrug2.lower())
        interaction = interaction[:index] + drug2.lower() + " (" + interaction[index:]
        index = index + len(resultDrug2) + len(drug2) + 2
        interaction = interaction[:index] + ")" + interaction[index:]

        return interaction
    return "Looks like there is no interaction between these drugs."

def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')" 

def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    #print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        #"data": data,
        #"contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(debug=False, port=port, host='0.0.0.0')
