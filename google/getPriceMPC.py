from googlefinance import getQuotes
import json
import time
import ROOT
import urllib2

price =39.0
googl=None
while price < 40.0 and price>32.00:
#while price>710.00:
    try:
        #googl = getQuotes('MPC')
        googl = getQuotes('NTDOY')
    except urllib2.HTTPError:
        print 'failed this round'
        time.sleep(5.0)
        continue
    print googl
    #print 'done'
    #googl= json.dumps(getQuotes('GOOGL'), indent=2)
    #for i in googl:
    #    print i
    #    if i.count('LastTradeWithCurrency'):
    #        price = i[i.find('LastTradeWithCurrency')+len('LastTradeWithCurrency'):]
    #        break
    #print price
    price = float(googl[0]['LastTradeWithCurrency'])
    print 'Price: ',price,' time: ',time.localtime()
    time.sleep(10.0)

print googl
c1 = ROOT.TCanvas("c1","testbeam efficiency",50,50,600,600);
c1.Draw()
c1.Update()
c1.WaitPrimitive()


