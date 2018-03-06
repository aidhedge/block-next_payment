import datetime
import json
import os
from ah_requests import AhRequest
from exceptions import NoAPIKeyPresent
from logger import Logger
LOG = Logger()
ah_request = AhRequest()

# CURRENCY_API_KEY = os.getenv('CURRENCY_API_KEY', None)
# if not CURRENCY_API_KEY:
#     raise NoAPIKeyPresent("Can't find 'CURRENCY_API_KEY' in the env variables", status_code=500) 


def get_risk_by_date(_list,pair,date):
    return [r for r in _list if r['date'] == date and r['pair'] == pair][0]['risk']

# How much is the increase/decrease (in %) from one number(start) 
# to another (end)
def percent_diff(start,end):
    result = 100*(end / start)-100
    return round(result, 3)

# Whats is the amount when increased/decreased by X% (pct)
def pct_change(number, pct):
    result = number*(pct/100)
    return round(result, 3)

def today(d=None):
    today = datetime.date.today()
    if d:
        datum = today + datetime.timedelta(days=d)
        return datum.strftime('%Y-%m-%d')
    else:
        return today.strftime('%Y-%m-%d')

def queryCurrencyApi(pair, date):
    CURRENCY_API_KEY = 'fd0c184ec8e0c57d3a22623274e87f89'
    url = "http://www.apilayer.net/api/historical?access_key={}&source={}&currencies={}&date={}".format(CURRENCY_API_KEY, pair[:3], pair[3:],date)
    #LOG.console(url)
    res = ah_request.get(url=url)
    res = res.json()
    return float(res['quotes'][pair])
    

def next(payload):
    project_data = payload['project_data']
    currency_risks = payload['currency_risks']
    project_start = project_data['project_start']
    todays_date = today()
    payments = []
    for t in project_data["transactions"]:
        currency_from = t["currency_from"]
        currency_to = t["currency_to"]
        pair = currency_from+currency_to
        #obj['direction'] = t['direction']
        #obj['pair'] = pair
        project_start_rate = queryCurrencyApi(pair=pair, date=project_start)
        todays_rate = queryCurrencyApi(pair=pair, date=today())
        pct_diff_since_start = percent_diff(start=project_start_rate, end=todays_rate)
        for p in t["payments"]:
            
            #data = json.loads('{"pair": "USDEUR","payment": [{"amount": 250000,"bar": "Budget"}, {"amount": 240000,"bar": "Projected outcome"}, {"amount": 150000,"bar": "Worst outcome"}, {"amount": 290000,"bar": "Best outcome"}]}')

            if p['date'] > todays_date:
                budget = p['amount']
                data = dict(pair=pair, date=p['date'], payment=[])
                obj = dict()

                obj.update(bar='Budget')
                obj.update(amount=budget)
                data['payment'].append(obj)

                obj = dict()
                obj.update(bar='Projected outcome')
                abs_change_since_start = pct_change(budget, pct_diff_since_start)
                #obj.update(diff=abs_change_since_start)
                obj.update(amount=budget + abs_change_since_start)
                data['payment'].append(obj)

                obj = dict()
                obj.update(bar='Minimum')
                abs_change_since_start = pct_change(budget, pct_diff_since_start)
                temp_amount = budget + abs_change_since_start
                pct_risk = get_risk_by_date(_list=currency_risks, pair=pair, date=p['date'])
                abs_change_with_risk = pct_change(temp_amount, pct_risk)
                obj.update(amount=temp_amount - abs_change_with_risk)
                data['payment'].append(obj)

                obj = dict()
                obj.update(bar='Maximum')
                abs_change_since_start = pct_change(budget, pct_diff_since_start)
                temp_amount = budget + abs_change_since_start
                pct_risk = get_risk_by_date(_list=currency_risks, pair=pair, date=p['date'])
                abs_change_with_risk = pct_change(temp_amount, pct_risk)
                obj.update(amount=temp_amount + abs_change_with_risk)
                data['payment'].append(obj)
                
                payments.append(data)
                

                #obj["payments"].append(dict(date=p['date'],pair=pair, budget=p['amount'] ))
                #pct_risk = get_risk_by_date(_list=currency_risks, pair=pair, date=p['date'])
        #data.append(obj)
    #LOG.console(payments)
    return payments  
       

