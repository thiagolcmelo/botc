# -*- coding: utf-8 -*-
#!/usr/bin/env python

from flask import Flask
from workers import sample

app = Flask(__name__)

@app.route('/')
def index():
    depth = sample.depth('ETHBTC')
    asks = depth['asks'][::-1]
    bids = depth['bids']

    table = ""

    for a in asks:
        table += "<tr><td></td><td></td><td>%s</td><td>%s</td></tr>" % (a[0], a[1])
    for b in bids:
        table += "<tr><td>%s</td><td>%s</td><td></td><td></td></tr>" % (b[1], b[0])
    html = """<html>
                <body>
                    <h1>Top 10 ETH-BTC BID-ASK</h1>
                    <table border='1'>
                        <thead>
                            <th>Bid Qtd</th>
                            <th>Bid Prc</th>
                            <th>Ask Prc</th>
                            <th>Ask Qtd</th>
                        </thead>
                        <tbody>%s</tbody>
                    </table>
                </body>
            </html>""" % table
    return html

if __name__ == '__main__':
    app.run(debug=True)