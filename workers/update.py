# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import requests
import json

def depth(symbol, limit=10):
    try:
        key = os.getenv('APIKEY')
        #secret = os.getenv('APISECRET')
        base_url = "https://api.binance.com"
        with requests.Session() as s:
            s.headers = {
                'X-MBX-APIKEY': key
            }
            mkt_depth = json.loads(s.get(base_url + ("/api/v1/depth?symbol=%s&limit=%d" % (symbol, limit))).text)
            time = json.loads(s.get(base_url + ("/api/v1/time")).text)
            mkt_depth['time'] = time['serverTime']
            return mkt_depth
    except:
        return {}

def trades(symbol, limit=10):
    try:
        key = os.getenv('APIKEY')
        #secret = os.getenv('APISECRET')
        base_url = "https://api.binance.com"
        with requests.Session() as s:
            s.headers = {
                'X-MBX-APIKEY': key
            }
            return json.loads(s.get(base_url + ("/api/v1/trades?symbol=%s&limit=%d" % (symbol, limit))).text)
    except:
        return {}
