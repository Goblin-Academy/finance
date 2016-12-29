import urllib2  # works fine with Python 2.7.9 (not 3.4.+)
import json
import time
 
def fetchPreMarket(symbol, exchange):
    link = "http://finance.google.com/finance/info?client=ig&q="
    url = link+"%s:%s" % (exchange, symbol)
    print url
    u = urllib2.urlopen(url)
    content = u.read()
    data = json.loads(content[3:])
    info = data[0]
    print info
    try:
        t = str(info["elt"])    # time stamp
        l = float(info["l"])    # close price (previous trading day)
        p = float(info["el"])   # stock price in pre-market (after-hours)
    except:
        t = str(info["ltt"])    # last trade time stamp
        l = float(info["l"])    # close price (previous trading day)
        pcl = float(info["pcls_fix"])   # previous close
        p = float(info["pcls_fix"])   # stock price in pre-market (after-hours). NOT RIGHT...FIX
        
    return (t,l,p)
 
 
p0 = 0
while True:
    #t, l, p = fetchPreMarket("AAPL","NASDAQ")
    #t, l, p = fetchPreMarket("CVX","NYSE")
    #t, l, p = fetchPreMarket("MSEX","NASDAQ")
    #t, l, p = fetchPreMarket("KMI","NYSE")
    #t, l, p = fetchPreMarket("VFINX","MUTF")
    #t, l, p = fetchPreMarket("LMT","NYSE")
    #t, l, p = fetchPreMarket("TWLO","NYSE")
    t, l, p = fetchPreMarket("NTDOY","OTCMKTS")
    #t, l, p = fetchPreMarket("GOOGL","NASDAQ")    
    if(p!=p0):
        p0 = p
        print("%s\t%.2f\t%.2f\t%+.2f\t%+.2f%%" % (t, l, p, p-l,
                                                 (p/l-1)*100.))
    time.sleep(60)
