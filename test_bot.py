from __future__ import print_function
from socket import *
from socket import error as socket_error
import sys
import json
import time


#declare global variables for tcp connection
TEAMNAME="EIEIO"
test_mode = True#False to run in production
test_exchange_index=0
prod_exchange_hostname="production"
port = 25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + TEAMNAME if test_mode else prod_exchange_hostname
serverstatus = 1

valbz = []
vale = []
xlf = []
bond = []
gs = []
ms = []
wfc = []
global orderid
orderid = 0
bond_fair = 1000
#establish TCP connection
def TCPconnect():
    global serverstatus
    s = socket(AF_INET,SOCK_STREAM)
    print ("Start connecting to the server...")
    s.connect((exchange_hostname, port))
    print ("Server Connection Established.")
    serverstatus = 1
    return s.makefile('rw', 1)

#read information from the exchange stream
def read_from_exchange(exchange):
    return json.loads(exchange.readline())

#post information to the exchange
def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

#collect price history
def server_info(exchange):
    global serverstatus
    count = 0
    print ("Updating Server info...")
    while(count<1000):
        info = read_from_exchange(exchange)
        if not info:
            break
        type = info["type"]
        if(type == "close"):
            serverstatus = 0;
            print ("Server closed.")
            return
        if(type == "trade"):
            
            if(info["symbol"] == "VALBZ"):
                valbz.append(info["price"])
                
            if(info["symbol"] == "VALE"):
                vale.append(info["price"])

            if (info["symbol"] == "XLF"):
                xlf.append(info["price"])

            if (info["symbol"] == "BOND"):
                bond.append(info["price"])

            if (info["symbol"] == "GS"):
                gs.append(info["price"])

            if (info["symbol"] == "MS"):
                ms.append(info["price"])

            if (info["symbol"] == "WFC"):
                wfc.append(info["price"])

        time.sleep(0.01)
        count += 1

def get_highest(arr):
    prices = []
    for i in range(len(arr)):
        prices.append(arr[i][0])
    highest = max(prices)
    return highest

def get_lowest(arr):
    prices = []
    for i in range(len(arr)):
        prices.append(arr[i][0])
    lowest = min(prices)
    return lowest

def mean(l):
    return sum(l)//len(l)

def ETF(exchange):
    prev = 15
    orderid = 10
    try:
        XLF_mean = mean(xlf[-prev:])
        bond_mean = mean(bond[-prev:])
        GS_mean = mean(gs[-prev:])
        MS_mean = mean(ms[-prev:])
        WFC_mean = mean(wfc[-prev:])

        if 10 * XLF_mean-50 > (3 * bond_mean + 2 * GS_mean + 3 * MS_mean + 2 * WFC_mean):
            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "XLF", "dir": "BUY",
                                         "price": XLF_mean + 1, "size": 100})
            orderid += 1
            write_to_exchange(exchange,
                              {"type": "convert", "order_id": orderid, "symbol": "XLF", "dir": "SELL", "size": 100})
            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "BOND", "dir": "BUY",
                "price": bond_mean - 1, "size": 30})

            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "GS", "dir": "BUY",
                                         "price": GS_mean - 1, "size": 20})

            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "MS", "dir": "BUY",
                                          "price": MS_mean - 1, "size": 30})

            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "WFC", "dir": "BUY",
                                         "price": WFC_mean - 1, "size": 20})

        else:
            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "BOND", "dir": "SELL",
                "price": bond_mean + 1, "size": 30})

            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "GS", "dir": "SELL",
                                         "price": GS_mean + 1, "size": 20})

            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "MS", "dir": "SELL",
                                          "price": MS_mean + 1, "size": 30})

            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "WFC", "dir": "SELL",
                                         "price": WFC_mean + 1, "size": 20})
            orderid += 1
            write_to_exchange(exchange,
                               {"type": "convert", "order_id": orderid, "symbol": "XLF", "dir": "BUY", "size": 100})

            orderid += 1
            write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "XLF", "dir": "SELL",
                                          "price": XLF_mean + 1, "size": 100})
            
    except:
        pass
        

def simple_bond(exchange):
    orderid = 1
    print("\n------------------------- BUY BOND!-------------------------\n")
    write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "BOND", "dir": "BUY","price": bond_fair+1000, "size": 10})
    print("\n------------------------- SELL BOND!-------------------------\n")
    write_to_exchange(exchange, {"type": "add", "order_id": orderid, "symbol": "BOND", "dir": "SELL","price": bond_fair-500, "size": 10})


def gs_trade(exchange):
    orderid = 2
    while True:
        info = read_from_exchange(exchange)
        if (info["type"] == "book" and info["symbol"] == "GS"):
            break
    lowest= get_lowest(info["buy"]);
    highest= get_highest(info["buy"]);
    print("\n------------------------- BUY GS!-------------------------\n")
    write_to_exchange(exchange,{"type": "add", "order_id": orderid, "symbol": "GS", "dir": "BUY", "price": highest, "size": 10})
    print("\n------------------------- SELL GS!-------------------------\n")
    
    write_to_exchange(exchange,{"type": "add", "order_id": orderid, "symbol": "GS", "dir": "SELL", "price": lowest, "size": 10})

def adr(exchange):
    orderid = 3
    print("\n------------------------- ADR!-------------------------\n")
    if (valbz[len(valbz)-1]<=vale[len(vale)-1]):
        write_to_exchange(exchange,{"type": "add", "order_id": orderid, "symbol": "VALE", "dir": "SELL", "price": vale[len(vale)-1]+1, "size": 10})
    else:
        write_to_exchange(exchange,{"type": "add", "order_id": orderid, "symbol": "VALE", "dir": "BUY", "price": vale[len(vale)-1], "size": 5})
        
        
#reconnect when the server is down
def reconnect(exchange):
    global serverstatus
    print ("\nMarket Closed. Reconnecting...\n")
    while(serverstatus == 0):
        try:
            print ("Reconnect: restablishing TCP connect")
            exchange = TCPconnect()
            write_to_exchange(exchange, {"type": "hello", "team": TEAMNAME.upper()})
            hello_from_exchange = read_from_exchange(exchange)
            print ("Reconnec: message received: " "%s" % hello_from_exchange)
            if(hello_from_exchange["type"] == "hallo"):
                serverstatus = 1
                print ("----------------Handshake Success!----------------")
            else:
                serverstatus = 0
                print ("----------------Handshake Error!----------------")
        except socket_error:
             print ("\r\nReconnect: socket error,do reconnect ")
             time.sleep(0.1)

def main():
    global serverstatus
    exchange = TCPconnect()
    print("Exchange Initialize Success.")

    write_to_exchange(exchange, {"type": "hello", "team": TEAMNAME.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    while(True):
        server_info(exchange)
        if(serverstatus == 1):
            simple_bond(exchange)
            gs_trade(exchange)
            adr(exchange)
            ETF(exchange)
        else:
            reconnect(exchange)

def initialize():
    print ("Initializing Test Mode: ")
    print ("   Test Mode: " "%s" % test_mode)
    print ("   Port: " "%s" % port)
    print ("   Hostname: " "%s" % exchange_hostname)

if __name__ == '__main__':
    initialize()
    while True:
         try:
             main()
         except socket_error:
             print ("\r\n----------------Main: socket error,do reconnect----------------")
             time.sleep(0.1)
