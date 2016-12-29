#from googlefinance import getQuotes
import yahoo_finance
from yahoo_finance import Share
import json
import time
import ROOT
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

        #c1 = ROOT.TCanvas("c1","testbeam efficiency",50,50,600,600);
        #c1.Draw()
        #c1.Update()
        #c1.WaitPrimitive()

    #print 'done'
    #googl= json.dumps(getQuotes('GOOGL'), indent=2)
    #for i in googl:
    #    print i
    #    if i.count('LastTradeWithCurrency'):
    #        price = i[i.find('LastTradeWithCurrency')+len('LastTradeWithCurrency'):]
    #        break
    #print price
t = time.localtime()
f = open('/Users/schae/testarea/finances/yahoo-finance/out/stocks_%s_%s_%s.txt' %(t.tm_year,t.tm_mon,t.tm_mday),'w')
#f = open('/Users/schae/testarea/finances/yahoo-finance/out/stocks_%s_%s_%sb.txt' %(t.tm_year,t.tm_mon,t.tm_mday),'w')

stock_list = [
        # Check stocks
        ['GOOGL',640.0,805.0], # google
        ['AMZN',450.0,700.0], # amazon
        ['AAPL',86.0,110.0], # apple
        ['MAT',25.0,40.0], # matel
        ['FB',93.0,130.0],
        ['MPC',30.0,48.0],  # marathon gas refinery
        ['CHK',4.0,7.0],  # cheseapeak
        ['KORS',45.0,60.0], # cosmetics
        ['NGL',5.0,15.0], # pipeline company
        ['CVX',78.0,100.0], # chevron
        #['UA',35.0,50.0], # under armour
        ['KR',35.0,50.0], # kroger. 1%
        ['TGT',65.0,85.0], # target. 3%        
        ['CVS',80.0,120.0], # CVS 1.6%
        ['TFM',25.0,35.0], # fresh market
        ['SFM',25.0,35.0], # sprouts farms
        ['WFM',25.0,35.0], # whole foods 1.7%
        ['CMG',400.0,600.0], # chipotle
        ['JACK',60.0,80.0], # JACK in the box
        ['WEN',9.0,15.0], # wendys
        ['PZZA',50.0,65.0], # papa johns
        ['MCD',100.0,150.0], # mc donalds - 3%
        ['DIN',60.0,120.0], # IHOP 3.7%
        ['DENN',7.0,15.0], # dennys - None
        ['F',10.0,15.0], # ford
        ['GM',25.0,40.0], # GM
        ['VZ',45.0,55.0], # verizon
        ['M',35.0,55.0], # macy's 
        ['MMM',132.0,170.0], # 3M
        ['TSO',50.0,105.0], # Tesoro
        ['NTI',20.0,30.0], # northern tier refinery. pays 15 % dividend
        ['INTC',25.0,34.0], # intel 3.55% dividend
        ['BCS',5.0,15.0], # barclays
        ['CS',5.0,15.0], # credit suisse banking stock. 6.7% dividend
        ['UBS',8.0,20.0], # ubs. 6.4% dividend
        ['DB',8.0,20.0], # deuchee bank.
        ['EBAY',20.0,30.0], # ebay
        ['UNH',100.0,130.0], # united health care
        ['CI',120.0,180.0], # health care. cigna
        ['PFE',25.0,38.0], # pfizer 4% dividend
        ['AET',75.0,120.0], # aetna 1% dividend
        ['HUM',145.0,190.0], # humara 1% dividend
        ['TFX',120.0,160.0], # teleflex 1% dividend. medical devices. wayne, PA
        ['LMAT',10.0,16.0], # le maitre 1% dividend. medical devices.
        ['MSEX',23.0,35.0], # NJ water company. 2.7% dividend
        ['WTR',30.0,40.0], # PA water company
        ['AWK',60.0,75.0], # canada water company
        ['AWR',20.0,53.0,'NYSE'], # american states water company
        ['PNR',20.0,53.0,'NYSE'], # pentair. partial water company that may grow
        ['DUK',70.0,100.0,'NYSE'], # DUKE energy. good electric stock. 3.8% dividend
        ['PPL',30.0,80.0,'NYSE'], # PPL comp. good electric stock. 4% dividend   
        ['XYL',40.0,75.0], # water tech company
        ['DPS',85.0,105.0], # dr pepper
        ['CINF',52.0,70.0], # insurance. cincy. 3% dividend
        ['GILD',75.0,110.0], # gilead biotech
        ['AMGN',140.0,170.0], # biotech. california. 2.7% dividend
        ['BIIB',200.0,300.0], # biotech. california. 0.0% dividend        
        ['ADR',50.0,85.0], # novartis
        ['SLP',6.0,15.0], # Simulations Plus. 1.8% dividend. biomedical
        ['GVP',2.0,3.0], # GSE nuclear, oil simulations company
        ['TAP',80.0,100.0], # molson beer. 1.8% dividend
        ['RTN',115.0,160.0], # ratheon. defense. 2.1% dividend
        ['VLO',45.0,70.0], # oil refinery 3.9% dividend
        ['ABBV',50.0,70.0], # pharma 4.0% dividend
        ['WDC',35.0,80.0], # western digital 4.2% dividend
        ['STX',30.0,50.0], # seagate 7% dividend
        ['BLK',200.0,500.0], # black rock 2.9% dividend.
        ['ADC',20.0,50.0], # real estate 4.9% dividend.
        ['NTRI',10.0,30.0], # nutrisystem 4.0% dividend.                 
        ['MET',30.0,60.0], # insurance 3.8% dividend.                 
        ['WY',20.0,35.0], # real estate 5.% dividend.                 
        ['RYN',20.0,35.0], # timber 3% dividend
        ['GLD',108.0,125.0], # gold
        ['DIA',120.0,200.0], # Dow jones 
        ['NDAQ',40.0,70.0], # nasdaq trader. 1.7% dividend
        ['TSN',40.0,70.0], # tyson foods. 1.% dividend
        ['GSK',35.0,70.0], # pharma. 6.% dividend          
        ['BMY',55.0,70.0], # Bristol-Myers Squibb. 6.% dividend          
        ['CRM',50.0,75.0], # salesforce. cloud platform service. 0.% dividend. nielsen is using them       
        ['ADP',75.0,100.0], # automatic data processing. cloud platform service. 2.% dividend. 
        ['INFY',15.0,25.0], # infosys. IT/software company. 2.% dividend          
        #['TCS',2000.0,2800.0], # TCS. IT/software company. 1.7% dividend          
        ['MCK',130.0,200.0], # mckessen. health care robotics and machine dosing. 0.7% dividend
        ['BHP',15.0,40.0], # BHP billington. mining company with 11% dividend. steve's pick. not so sure about this one
        ['BP',20.0,45.0], # british patroleum.  8.2% dividends
        #['NEE',100.0,140.0], # florida electrical company.  2.7% dividends        
        ['ABX',8.0,20.0], #Barrick Gold mining company 0.6% dividend
        ['SLW',10.0,20.0], # Silver Wheaton Corp 1.6% dividend
        ['EXK',1.0,4.0], # Silver mine 22% dividend
        ['HCHDF',0.2,2.0], # Silver mine 22% dividend
        ['GG',10.0,20.0], # Goldcorp mining company 1.6% dividend
        ['NEM',16.0,35.0], # Newmont Mining gold mining company 0.4% dividend
        ['AUY',1.3,3.4], # Yamana Gold mining company 2.5% dividend Canada
        ['NOA',1.3,4.0], # Mining US. 2% dividend.
        ['HMY',2.3,5.0], # Harmony gold Mining US.
        ['GFI',3.3,6.0], # Gold fields unlimited. south african gold
        ['EGO',3.3,6.0], # eldarado gold.
        ['BTG',1.3,4.0], # b2gold
        ['VALE',3.3,6.0], # mineral miner in brazil 2.dividend
        ['KGC',1.3,3.8], # KinCross Gold mining company 0.0% dividend Canada
        ['CSCO',15.0,35.0], # cisco. 3.7%
        ['KMI',10.0,40.0], # kinder morgan. Berkshire hathaway is investing in them. 2.9%

        ['GNOW',0.1,2.0], # urgent care nano cap. check carefully
        ['ENSG',10.0,25.0], # urgent care small cap. check carefully
        ['ADPT',45.0,70.0], # urgent care small cap. check carefully. no dividend
        ['EVHC',18.0,33.0], # urgent care mid cap. check carefully. no dividend
        ['LPNT',60.0,80.0], # urgent care mid cap. check carefully. no dividend
        ['THC',23.0,30.0], # urgent care/intensive care mid cap. check carefully. no dividend

        ['SHAK',33.0,60.0], # shake shack.
        ['UAL',45.0,70.0], # united airlines

        ['VOO',100.0,200.0], # vanguard MUTF
        ['VFINX',100.0,200.0], # vanguard MUTF
        ['VFIAX',100.0,200.0], # vanguard MUTF
        ['VPU',75.0,125.0], # vanguard utilities, 3.3% dividend                
        ['RYU',50.0,100.0], # equal weight utilities,
        ['VBK',50.0,170.0], # vanguard small cap growth
        ['VYM',60.0,90.0], # vanguard large cap mutual fund 3.1% dividend
        ['IVE',70.0,130.0], # ishare mutual fund 
        ['TSLA',200.0,300.0], # ishare mutual fund 
        ['BBBY',40.0,70.0], # bed bath and beyond
        ['TWTR',10.0,20.0], # twitter
        ['S',2.0,5.0], # sprint
        ['TMUS',2.0,5.0], # t-mobile
        ['HOG',40.0,55.0], # 3% dividend harley davidson
        ['PIR',5.0,10.0], # 3% dividend pier 1 imports
        ['DDD',15.0,25.0], # 3D printing manufacturer
        ['XONE',10.0,15.0], # 3D printing manufacturer exone
        ['SSYS',20.0,40.0], # 3D printing manufacturer exone
        ['AMAT',13.0,27.0], # chip gear manufacturer
        ['GPRO',10.0,19.0], # go pro stock
        ['QCOM',40.0,65.0], # qualcomm - starting in drone market. 4% dividend
        ['IXYS',10.0,15.0], # parts manufacturer for drones
        ['INVN',4.0,10.0], # parts manufacturer for drones. motion control     
        ['STM',4.0,8.0], # parts manufacturer for drones. motion control. geneva based. won apple smart watch bid. 7.4% dividend
        ['NXPI',70.0,100.0], # semi-conductor manufacturer
        ['TXN',50.0,70.0], # texas instraments. semi-conductor manufacturer
        ['INFN',10.0,20.0], # infera semi-conductor manufacturer.
        ['LMT',150.0,300.0], # lockheed martin. 2.92
        ['BA',100.0,150.0], # lockheed martin. 2.92
        ['NOC',170.0,250.0], # northrop gruman. 2.92
        ['GBSN',3.0,8.0], # genetics testing company
        ['AMAG',20.0,50.0], # pharma in iron deficiency
        ['MOH',60.0,80.0], # Molina health. zach's #1
        ['CRL',70.0,100.0], # Charles river health. zach's #2
        ['AIRM',30.0,50.0], # air drop pharma. zach's #2
        ['PRXL',60.0,71.0], # paralex medical supplies        
        ['FPRX',40.0,60.0], # therapuetics - rated a buy.        
        ['EBS',30.0,50.0], # emergent bio solutions. high zacks rating
        ['FCSC',1.0,3.0], # fibrocell. random pharma
        ['GENE',2.0,3.0], # genetics testing company
        ['OPK',8.0,13.0], # genetics testing company. is subsidiary
         ['RGLS',6.0,10.0], # bio pharma
         ['DGX',50.0,90.0], # pharma testing company
         ['ORPN',2.0,5.0], # bio pharma
         ['VIVO',15.0,25.0], # malaria indicator stock. Meridian
         ['XON',30.0,50.0], # zika indicator stock. Intrexon
         ['INO',7.0,15.0], # zika indicator stock. Inovio
         ['NLNK',15.0,25.0], # zika indicator stock. Newlink        
         ['CERS',4.0,8.0], # zika indicator stock. ceries        
         ['SNY',30.0,50.0], # zika indicator stock. sanofi. dividend 3.72%
         ['JCP',5.0,15.0], # JC pennies.
         ['DQ',20.0,35.0], # Daqo New Energy Corp. zacks rated high
         ['CAT',60.0,90.0], # Catepillar, 3.8% dividend. most shorted
         ['CBA',6.0,9.0], # clearbridge. energy company, 10% dividend. 
         ['UTX',80.0,120.0], # united  technolgy. airplane builder most shorted, 2.4% dividend.
         ['HON',95.0,130.0], # honeywell. 2%
         ['V',65.0,100.0], # visa. 0.7%
         ['MO',50.0,70.0], # tobacco company. Altria 3%
         ['RAI',40.0,60.0], # reynolds stock. tobacco. 3%
         ['TAP',80.0,120.0], # molson-coors. 1.7%         
         ['STZ',140.0,180.0], # constellation drinks stock. 1%
         ['BWLD',100.0,180.0], # BW3's
         ['TXRH',35.0,80.0], # texas road house
         ['CGNX',30.0,80.0], # machine vision. 0.8%
         ['CFX',30.0,80.0], # colfax?
         ['PCLN',1000.0,1500.0], # priceline
         ['TRIP',50.0,70.0], # trip adviser
         ['SWHC',10.0,30.0], # smith and wessin
         ['RGR',40.0,70.0], # ruger 2.5% dividend
         ['OLN',10.0,30.0], # winchester++ 3% dividend
         #['TWLO',20.0,40.0], # twilio
         ['BKS',7.0,15.0], # barnes & nobles. 5% dividend
         ['DNKN',35.0,55.0,'NASDAQ'], # dunkin doughnuts. 2.7% dividend         
         ['SBUX',35.0,75.0,'NASDAQ'], # starbucks. 1.5% dividend         
         ['KKD',15.0,30.0,'NYSE'], # krispy kreme 
         ['JVA',4.0,10.0,'NASDAQ'], # JAVA. pure coffee holding
         ['VIAB',30.0,80.0,'NASDAQ'], # viacom 3.7% dividend

         ['^DJI',17.0e3,22.0e3,'NYSE'], # DJIA
         ['XTN',30.0,80.0,'NYSE'], # S&P transport
         ['DJTA',7.0e3,10.0e3,'NYSE'], # DJIA transport
         ['VIOO',60.0,150.0,'NYSE'], # small cap
         ['MDY',200.0,300.0,'NYSE'], # mid cap
         ['GS',150.0,300.0,'NYSE'], # Goldman saks. 1% dividend
         ['JPM',65.0,120.0,'NYSE'], # JPM chase. 2% dividend
         ['PNC',90.0,150.0,'NYSE'], # PNC bank. 2% dividend
         ['VGT',90.0,150.0,'NYSEARCA'], # Vanguard information tech. 1.4% dividend                           
         #['NTDOY',30.0,80.0,'OTCMKTS'], # viacom 3.7% dividend         
        #['SPY',60.0,90.0], # spyder large cap mutual fund
        #['VIG',60.0,90.0], # vanguard large cap mutual fund 3.1% dividend
        #['WTI',20.0,35.0], # west texas intermediate. crude oil
        #['NDX',2000.0,5000.0], # nasdaq index  
        ]
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
    pickle.dump( stocks_info, open( '/Users/schae/testarea/finances/yahoo-finance/out/stocks_%s_%s_%s.p' %(t.tm_year,t.tm_mon,t.tm_mday), "wb" ) )
    sys.exit(0)
else:
    history_stocks_info = pickle.load( open( "/Users/schae/testarea/finances/yahoo-finance/out/stocks_2016_2_5.p", "rb" ) )

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

