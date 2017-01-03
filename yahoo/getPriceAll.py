#from googlefinance import getQuotes
import yahoo_finance
from yahoo_finance import Share
import json
import time
import base
import urllib2
import datetime
import send_sms
import sys
import pickle
import MA_analysis
import MACD_analysis
import RSI_analysis
import correl_analysis
import Vol_analysis
import getCurrency
import socket

#0 make the current script stable enough to run all day. -> DONE Perhaps compress the data saved ->
#1 pickle the list of messages. Changes in stock prices. reload them when the code is restarted -> DONE
#1b add percentage change from now and on the day. -> DONE
#2 use the yahoo data to get the 52 week high and low for the upper and lower bounds -> 
#2b implement pre and post market trading
#3 something more advanced?

out_path = base.out_path
out_file_type = base.out_file_type
Pickle=False
SENDMESSAGE=False
LIST_OF_MESSAGES={} #ticker and price

#----------------------
def RequestStocks(flist, fout):
    slist=[]
    for i in range(0,len(flist)):
        try:
            #print flist[i]
            #sys.stdout.flush()
            googl = Share(flist[i])
            slist+=[googl]
        except (urllib2.HTTPError,urllib2.URLError):
            fout.write( 'Failed this round!!!! \n')
            fout.flush()
            time.sleep(5.0)
            i-=1
    #print slist
    #sys.stdout.flush()
    return slist

#----------------------
def check(googl, fout, ticker='GOOGL',min_price=710.0, max_price=805.0, history_stock=None):
    price =(max_price+min_price)/2.0
    try:
        googl.refresh()
        price =-1.0
        day_start_price=-1.0
        try:
            price = float(googl.get_price().strip('CHF').strip('GBX'))
            day_start_price = float(googl.get_prev_close().strip('CHF').strip('GBX'))
        except:
            print 'ticker...did not get price: ',ticker
            print 'price: ',googl.get_price()
            print 'googl.get_prev_close(): ',googl.get_prev_close()
        percent_change = 0.0
        if day_start_price>0.0:
            #\033[1;31mbold red text\033[0m\n
            #\033[1;32mbold green text\033[0m\n            
            percent_change=100.0*(price-day_start_price)/day_start_price
        line = 'Price for '
        if percent_change>0.0:
            line+='\033[1;32m '+ticker+' \033[0m is: %0.2f and change is \033[1;32m %0.2f \033[0m' %(price,percent_change)
        else:
            line+='\033[1;31m '+ticker+' \033[0m is: %0.2f and change is \033[1;31m %0.2f \033[0m' %(price,percent_change)
        # change in recent history
        if history_stock!=None:
            chg = 0.0
            if history_stock.get_price()>0.0:
                chg = 100.0*(price-float(history_stock.get_price()))/float(history_stock.get_price())
            line+='. Was originally %0.2f. Change: %0.2f' %(float(history_stock.get_price()), chg)            
        fout.write(line+'\n');
    except (urllib2.HTTPError,AttributeError,yahoo_finance.YQLQueryError,urllib2.URLError):
        fout.write( 'Failed this round!!!! for '+ticker+' \n')
        fout.flush()
        time.sleep(5.0)
        return False

    if not (price < max_price and price>min_price):
        fout.write( 'Found what we were looking for....\n' )
        print googl
        message = 'yahoo finance. Prices delayed by 15 min. Stock: '+ticker+' is at %0.2f. ' %price
        if price<min_price: 
            message+='This is below threshold of %0.2f.' %min_price
            message+=' Recommend to BUY stock.'
        if price>max_price: 
            message+='This is above threshold of %0.2f.' %max_price
            message+=' Recommend to Sell stock.'

        if ticker in LIST_OF_MESSAGES:
            if (LIST_OF_MESSAGES[ticker]*0.98)>price and price<min_price:
                # resend if change is larger than 2 % in decrease from last message
                LIST_OF_MESSAGES[ticker] = price
            elif (LIST_OF_MESSAGES[ticker]*1.02)<price and price>max_price:
                # resend if change is larger than 2 % in decrease from last message
                LIST_OF_MESSAGES[ticker] = price            
            else:
                # otherwise no new message should be sent
                return
        else:
            LIST_OF_MESSAGES[ticker] = price
            
        if price>0.0:
            if SENDMESSAGE:
                send_sms.sendMessage(message)

    #print 'done'
    #googl= json.dumps(getQuotes('GOOGL'), indent=2)
    #for i in googl:
    #    print i
    #    if i.count('LastTradeWithCurrency'):
    #        price = i[i.find('LastTradeWithCurrency')+len('LastTradeWithCurrency'):]
    #        break
    #print price
t = time.localtime()
f = open(out_path+'/out/stocks_%s_%s_%s.txt' %(t.tm_year,t.tm_mon,t.tm_mday),'w')
#f = open(out_path+'/out/stocks_%s_%s_%sb.txt' %(t.tm_year,t.tm_mon,t.tm_mday),'w')

stock_list = base.stock_list

if False:
    stock_list = [
        # Check stocks
        ['GOOGL',640.0,805.0,'NASDAQ'], # google
        ['AMZN',450.0,700.0,'NASDAQ'], # amazon
        ['AAPL',86.0,110.0,'NASDAQ'], # apple
        ]
        
# Collect stock information
stock_names = []
for i in stock_list:
    stock_names+=[i[0]]
stocks_info=None
while stocks_info==None:
    try:
        stocks_info = RequestStocks(stock_names, f)
    except (socket.gaierror):
        print 'socket.gaierror...retrying in 5s'
        stocks_info=None
        time.sleep(5.0)    
# check Currency
getCurrency.Run()

history_map={}
# run M/A analysis at the beginning of the day
if True:
    ma_analysis_summary=[]
    itern=0
    maline=''
    for s in stocks_info:
        myinfo,mahistory = MA_analysis.runWithTicker(s)
        if len(myinfo)==0:
            print 'Failed... for ',s
            continue
        history_map[stock_names[itern]]=mahistory
        if myinfo[0][1]<4:
            line = stock_names[itern]+' '+myinfo[0][0]+' %s days ago' %(myinfo[0][1])
            ma_analysis_summary+=[line]
        if myinfo[1][1]<4:
            line = stock_names[itern]+' '+myinfo[1][0]+' %s days ago' %(myinfo[1][1])
            ma_analysis_summary+=[line]
        if len(myinfo)>5:
            maline+='%s,%0.2f,%0.2f,%0.2f,%0.2f\n' %(stock_names[itern],myinfo[2],myinfo[3],myinfo[4],myinfo[5])
        else:
            print 'ERROR - not enough info: ',myinfo
        itern+=1            
        #print maline
    print 'Stock info from M/A analysis: ',ma_analysis_summary
    if len(ma_analysis_summary)>0:
        ma_message=''
        for ma in ma_analysis_summary:
            ma_message+=ma+'\n'
        #send_sms.sendMessage(ma_message)
    # write out the Moving averages for later checking
    fma = open('ma/ma_limits.txt','w')
    fma.write(maline)
    fma.close()
    #sys.exit(0)
# end M/A analysis
# run MACD analysis at the beginning of the day
if True:
    macd_analysis_summary=[]
    itern=0
    for s in stocks_info:
        mahistory=None
        if stock_names[itern] in history_map:
            mahistory=history_map[stock_names[itern]]
        myinfo = MACD_analysis.runWithTicker(s,history=mahistory)
        macd_analysis_summary+=[myinfo]
        itern+=1
    print '---------------'
    print '---MACDResults-----'
    print '---------------'
    #rsi_results=RSI_analysis.sortMe(rsi_list)
    for r in macd_analysis_summary:
        if not r or len(r)<4:
            print 'Missing content: ',r
            continue
        if not r[1]:
            print 'first: ',r[1]
            continue
        if (r[1]>-1.0 and r[1]<3.0):
            print 'MACDBUY: ',r
        elif (r[2]>-1.0 and r[2]<3.0):
            print 'MACDSELL:',r
    print '---------------'
    print '---------------'
    print '---------------'  
        
    #sys.exit(0)
# end MACD analysis
# run RSI analysis at the beginning of the day
if True:
    itern=0
    rsi_list = []
    for s in stocks_info:
        mahistory=None
        if stock_names[itern] in history_map:
            mahistory=history_map[stock_names[itern]]
        myinfo = RSI_analysis.runWithTicker(s,history=mahistory)
        itern+=1
        rsi_list+=[myinfo]
    print '---------------'
    print '---Results-----'
    print '---------------'
    rsi_results=RSI_analysis.sortMe(rsi_list)
    for r in rsi_results:
        print r
    print '------Stochastic-------'
    rsi_results=RSI_analysis.sortMe(rsi_list,80.0,20.0,'Stochastic',4) 
    for r in rsi_results:
        print r    
    print '------Stochastic MA-------'
    rsi_results=RSI_analysis.sortMe(rsi_list,80.0,20.0,'Stochastic MA',7) 
    for r in rsi_results:
        print r
    print '---------------'    
    print '---------------'
    print '---------------'
    frsi = open('rsi/rsi_limits.txt','w')
    rline=''
    for i in rsi_list:
        for j in i:
            try:
                rline+='%0.3f,'%(j)
            except:
                rline+=j+','
        rline+='\n'
    frsi.write(rline)
    frsi.close()
    #sys.exit(0)
# end RSI analysis
if True:
    itern=0
    for s in stocks_info:
        mahistory=None
        if stock_names[itern] in history_map:
            mahistory=history_map[stock_names[itern]]
        ref_history=None
        if 'DIA' in history_map:
            ref_history=history_map['DIA']            
        myinfo = correl_analysis.runWithTicker(s,ref_hist=ref_history,history=mahistory)
        itern+=1
    #sys.exit(0)
#END
if True:
    itern=0
    for s in stocks_info:
        mahistory=None
        if stock_names[itern] in history_map:
            mahistory=history_map[stock_names[itern]] 
        myinfo = Vol_analysis.runWithTicker(s,history=mahistory)
        itern+=1
    #sys.exit(0)
#END
# pickle file for historical data from one date
history_stocks_info=None
if Pickle:
    pickle.dump( stocks_info, open( out_path+'/out/stocks_%s_%s_%s.p' %(t.tm_year,t.tm_mon,t.tm_mday), "wb" ) )
    sys.exit(0)
else:
    history_stocks_info = pickle.load( open( out_path+"/out/stocks_2016_2_5.p", "rb" ) )

while True:

    t = time.localtime()
    f.write('Time: %s:%s:%s\n' %(t.tm_hour, t.tm_min, t.tm_sec))
    dt = datetime.date(t.tm_year, t.tm_mon, t.tm_mday)
    #print dt.today()
    #sys.stdout.flush()
    #print dt.today().day
    #print time.tzname[0]
    if t.tm_wday==5:
        f.write( 'saturday\n') 
        break
    if t.tm_wday==6:
        f.write( 'sunday\n')
        break
    if 'CET' == time.tzname[0].strip():
        if t.tm_hour<14.0 or t.tm_hour>21.0:
            f.write( 'market is not in session\n')
            break;
    elif 'EST' == time.tzname[0].strip():
        if t.tm_hour<8.0 or t.tm_hour>15.0:
            f.write( 'market is not in session\n')
            break;
                 
    # Check stocks
    for s in range(0,len(stocks_info)):
        history_stock = None
        if s<len(history_stocks_info):
            if history_stocks_info[s]._key == stocks_info[s]._key:
                history_stock=history_stocks_info[s]
        
        check(stocks_info[s], f, stock_list[s][0], stock_list[s][1], stock_list[s][2], history_stock)
    
    f.write('------------------------------------------\n')
    #print 'flush'
    #sys.stdout.flush()
    f.flush()
    #print 'flushed'
    #sys.stdout.flush()
    time.sleep(30.0)

f.close()

