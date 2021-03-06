# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from workers import sample
from workers.update import depth, trades

########################################################################
dbhost = os.getenv("DBHOST")
dbport = os.getenv("DBPORT")
dbuser = os.getenv("DBUSER")
dbpass = os.getenv("DBPASS")
dbname = os.getenv("DBNAME")
########################################################################
app = Flask(__name__)

########################################################################
con_str = 'postgresql+psycopg2://%s:%s@%s:%s/%s' \
    % (dbuser, dbpass, dbhost, dbport, dbname)
print(con_str)
app.config['SQLALCHEMY_DATABASE_URI'] = con_str
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pair = db.Column(db.String, nullable=True)
    binance_id = db.Column(db.Integer, unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    qty = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    is_buyer_maker = db.Column(db.Boolean)
    is_best_match = db.Column(db.Boolean)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pair = db.Column(db.String, nullable=True)
    binance_id = db.Column(db.Integer, nullable=False)
    bid_price = db.Column(db.Float, nullable=False)
    bid_qty = db.Column(db.Float, nullable=False)
    ask_price = db.Column(db.Float, nullable=False)
    ask_qty = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

########################################################################

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

@app.route('/update')
def update():
    messages = []
    for pair in ['ETHBTC', 'BTCUSDT']:
        ######## order book
        try:
            book = depth(pair)
            binance_id = (book.get('lastUpdateId') and int(book['lastUpdateId'])) or 0
            time = datetime.fromtimestamp(float(book['time']) / 1000)
            for bid, ask in zip(book['bids'], book['asks']):
                b = Book(binance_id=binance_id, time=time,
                    pair=pair,
                    bid_price=float(bid[0]),
                    bid_qty=float(bid[1]),
                    ask_price=float(ask[0]),
                    ask_qty=float(ask[1]))
                db.session.add(b)
            db.session.commit()
        except Exception as err:
            messages.append('error getting order book: %s' % str(err))
        ######## last trades
        try:
            mkt_trades = trades(pair, 100)
            for trade in mkt_trades:
                binance_id = (trade.get('id') and int(trade['id'])) or 0
                time = datetime.fromtimestamp(float(trade['time']) / 1000)
                t = Trade()
                t = Trade(binance_id=binance_id, time=time,
                    pair=pair,
                    price=float(trade['price']),
                    qty=float(trade['qty']),
                    is_buyer_maker=trade['isBuyerMaker'],
                    is_best_match=trade['isBestMatch'])
                db.session.add(t)
            db.session.commit()
        except Exception as err:
            messages.append('error getting last trades: %s' % str(err))
    return '\n'.join(messages)

if __name__ == '__main__':
    app.run(debug=True)
    #db.create_all()
