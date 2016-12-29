from googlefinance import getQuotes
import json
import time
import ROOT
import urllib2
import datetime
import send_sms
import sys
import pickle
REPORT_SELL_ONLY_IF_I_OWN=True
#0 make the current script stable enough to run all day. Perhaps compress the data saved
#1 pickle the list of messages. Changes in stock prices. reload them when the code is restarted
#1b add percentage change from now and on the day.
#2 use the yahoo data to get the 52 week high and low for the upper and lower bounds
#3 something more advanced?
Pickle=False
SENDMESSAGE=False
LIST_OF_MESSAGES={} #ticker and price
#----------------------
class Data():
    def __init__(self,tick,vals):
        self.ticker = tick
        self.rsi = float(vals[1])
        self.rsi_overbought_price = float(vals[2])
        self.rsi_underbought_price = float(vals[3])
        self.stoch = float(vals[4])
        self.stoch_overbought_price = float(vals[5])
        self.stoch_underbought_price = float(vals[6])
        self.stocks_i_own = ['SLP','HOG'] # don't print to sell unless I own them
        if not REPORT_SELL_ONLY_IF_I_OWN:
            self.stocks_i_own =[]

        self.ma_20day = -1.0
        self.ma_50day = -1.0
        self.ma_100day = -1.0
        self.ma_200day = -1.0
    def AddMA(self, vals):
        if len(vals)>4:
            self.ma_20day = float(vals[1].strip())
            self.ma_50day = float(vals[2].strip())
            self.ma_100day = float(vals[3].strip())
            self.ma_200day = float(vals[4].strip().rstrip('\n'))

    def AddMAString(self, price):
        rline=''
        if price<0.0:
            return rline
        if self.ma_20day>0.0:
            if self.ma_20day>price:
                below=100.0*(price-self.ma_20day)/self.ma_20day
                rline+=' Rel to 20d:\033[1;31m %0.1f \033[0m' %(below)
            else:
                above=100.0*(price-self.ma_20day)/self.ma_20day
                rline+=' Rel to 20d:\033[1;32m +%0.1f \033[0m' %(above)                
        if self.ma_50day>0.0:
            if self.ma_50day>price:
                below=100.0*(price-self.ma_50day)/self.ma_50day
                rline+=' 50d:\033[1;31m %0.1f \033[0m' %(below)
            else:
                above=100.0*(price-self.ma_50day)/self.ma_50day
                rline+=' 50d:\033[1;32m +%0.1f \033[0m' %(above)                
        if self.ma_200day>0.0:
            if self.ma_200day>price:
                below=100.0*(price-self.ma_200day)/self.ma_200day
                rline+=' 200d:\033[1;31m %0.1f \033[0m' %(below)
            else:
                above=100.0*(price-self.ma_200day)/self.ma_200day
                rline+=' 200d:\033[1;32m +%0.1f \033[0m' %(above)                
        return rline
    def IsRsiOS(self, p):
        return (self.rsi_overbought_price < p)
    def IsRsiUS(self, p):
        return (self.rsi_underbought_price > p)
    def IsStochOS(self, p):
        return (self.stoch_overbought_price < p)
    def IsStochUS(self, p):
        return (self.stoch_underbought_price > p)
    def Decision(self,p):
        line = ''
        if p<0.0:
            return line
        if self.ticker in self.stocks_i_own:
            if self.IsRsiOS(p):
                line+='   SELL-> '+self.ticker+' RSI overSold: %0.2f currentPrice: %0.2f \n' %(self.rsi_overbought_price,p)
            if self.IsStochOS(p):
                line+='   SELL-> '+self.ticker+' STOCHASTIC overSold: %0.2f currentPrice: %0.2f \n' %(self.stoch_overbought_price,p)
        if self.IsRsiUS(p):
            line+='   BUY-> '+self.ticker+' RSI underSold: %0.2f currentPrice: %0.2f \n' %(self.rsi_underbought_price,p)
        if self.IsStochUS(p):
            line+='   BUY-> '+self.ticker+' STOCHASTIC underSold: %0.2f currentPrice: %0.2f \n' %(self.stoch_underbought_price,p)
        return line
#----------------------
def GetLimits():
    vv = {}
    fin = open('/Users/schae/testarea/finances/yahoo-finance/rsi/rsi_limits.txt','r')
    for f in fin:
        if len(f.strip())==0:
            continue
        vals = f.split(',')
        vv[vals[0]] = Data(vals[0],vals)
    fin.close()

    finma = open('/Users/schae/testarea/finances/yahoo-finance/ma/ma_limits.txt','r')
    for f in finma:
        if len(f.strip())==0:
            continue
        vals = f.split(',')
        if vals[0] in vv:
            vv[vals[0]].AddMA(vals)
    finma.close()
    
    return  vv

#----------------------
def RequestStocks(flist, fout):
    googl=None
    try:
        len_list = int(len(flist)/98)
        for p in range(0,len_list+1):
            my_list = flist[98*p:98*(p+1)]
            if p==len_list:
                my_list = flist[98*p:len(flist)]
            #print my_list
            googl_tmp = getQuotes(my_list)
            if googl==None:
                googl=googl_tmp
            else:
                for i in googl_tmp:
                    googl+=[i]
    except (urllib2.HTTPError,urllib2.URLError):
        fout.write( 'Failed this round!!!! \n')
        fout.flush()
        time.sleep(5.0)
        return []
    return googl
#----------------------
def fetchPreMarket(fout, symbol, exchange):
    #print 'premarket ',symbol
    link = "http://finance.google.com/finance/info?client=ig&q="
    url = link+"%s:%s" % (exchange, symbol)
    try:
        u = urllib2.urlopen(url)
        content = u.read()
        data = json.loads(content[3:])
        info = data[0]
    except (urllib2.HTTPError,urllib2.URLError):
        fout.write( 'Failed this round for %s!!!! \n' %(symbol))
        fout.flush()
        time.sleep(5.0)
        return (-1.0,-1.0,-1.0)
    #print info
    try:
        if "elt" in info:
            t = str(info["elt"])    # time stamp
            l = float(info["l"])    # close price (previous trading day)
            p = float(info["el"])   # stock price in pre-market (after-hours)
        else:
            fout.write( 'NOT CORRECT this round for %s!!!! \n' %(symbol))
            t = str(info["ltt"])    # last trade time stamp
            l = float(info["l"])    # close price (previous trading day)
            pcl = float(info["pcls_fix"])   # previous close
            p = float(info["pcls_fix"])   # stock price in pre-market (after-hours). NOT RIGHT...FIX
    except:
        return (-1.0,-1.0,-1.0)
    return (t,l,p)

#----------------------
def check(flist, fout, ticker='GOOGL',min_price=710.0, max_price=805.0, stock_exchange='NYSE', history_stock_info=None, isPreMarket=False, map_for_rsi={}):
    price =(max_price+min_price)/2.0
    googl=None
    if flist==None:
        fout.write( 'List of stocks is empty!!!! \n')
        fout.flush()
        return
    for a in flist:
        if a['StockSymbol']==ticker:
            googl=a
            break

    if googl==None or not googl:
        print 'error broker ticker: ',ticker
        sys.stdout.flush()
        return False
    price=0.0
    day_start_price=0.0
    #print ticker
    try:
        price = float(googl['LastTradeWithCurrency'])
        day_start_price=-1.0
        if len(googl['PreviousClosePrice'].strip())>0.0:
            day_start_price= float(googl['PreviousClosePrice'])
    except ValueError:
        #print 'CRASH: ',googl['LastTradeWithCurrency']
        #print 'CRASH:',googl['PreviousClosePrice']
        #sys.stdout.flush()
        if googl['LastTradeWithCurrency'].strip()=='':
            return False
        price = float(googl['LastTradeWithCurrency'].strip('CHF').strip('$').replace('&#8364;','').strip('GBX').replace(',',''))
        day_start_price= float(googl['PreviousClosePrice'].strip('CHF').strip('$').strip('GBX').replace('&#8364;','').replace(',',''))
        
    if isPreMarket:
        a,b,c=fetchPreMarket(fout, ticker, stock_exchange)
        price = c
        if c<0.0:
            return False
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
    #line='Price for '+ticker+' is: %0.2f ' %price #,' at time: ',time.localtime()
    if history_stock_info!=None:
        hist = None
        for a in history_stock_info:
            if a['StockSymbol']==ticker:
                hist=a
                break
        if hist!=None:
            old_price = float(hist['LastTradeWithCurrency'])
            old_price_perct_change=0.0
            if old_price>0.0:
                old_price_perct_change = 100.0*(price-old_price)/old_price
            if old_price_perct_change>0.0:
                line+='. First followed at %0.2f. Change of \033[1;32m +%0.2f \033[0m.' %(old_price,old_price_perct_change)
            else:
                line+='. First followed at %0.2f. Change of \033[1;31m %0.2f \033[0m.' %(old_price,old_price_perct_change)
    # check the position relative to the MA
    if ticker in map_for_rsi:
        line+=map_for_rsi[ticker].AddMAString(price)
    fout.write(line+'\n')
    # check the position relative to RSI
    if ticker in map_for_rsi:
        fout.write(map_for_rsi[ticker].Decision(price))
    if not (price < max_price and price>min_price):
        fout.write( 'Found what we were looking for....\n' )
        print googl
        message = 'Stock: '+ticker+' is at %0.2f. ' %price
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
f = open('/Users/schae/testarea/finances/googlefinance/out/stocks_%s_%s_%s.txt' %(t.tm_year,t.tm_mon,t.tm_mday),'w')
#f = open('/Users/schae/testarea/finances/googlefinance/out/stocks_%s_%s_%sb.txt' %(t.tm_year,t.tm_mon,t.tm_mday),'w')

history_stock_info=None
if not Pickle:
    #history_stock_info = pickle.load( open( "/Users/schae/testarea/finances/googlefinance/out/stocks_2016_2_5.p", "rb" ) )
    history_stock_info = pickle.load( open( "/Users/schae/testarea/finances/googlefinance/out/stocks_2016_3_10.p", "rb"))
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
    isPreMarket=False
    if 'CET' == time.tzname[0].strip():
        if t.tm_hour<13.0 or t.tm_hour>23.0:
            f.write( 'market is not in session\n')
            break;
        if (t.tm_hour<15.0 or (t.tm_hour==15 and t.tm_min<30)) or t.tm_hour>22.0:
            isPreMarket=True
    elif 'EST' == time.tzname[0].strip():
        if t.tm_hour<7.0 or t.tm_hour>16.0:
            f.write( 'market is not in session\n')
            break;
        if (t.tm_hour<9.0 or (t.tm_hour==9 and t.tm_min<30)) or t.tm_hour>15.0:
            isPreMarket=True
            

    stock_list = [
        # Check stocks
        ['GOOGL',640.0,805.0,'NASDAQ'], # google
        ['AMZN',450.0,700.0,'NASDAQ'], # amazon
        ['AAPL',86.0,110.0,'NASDAQ'], # apple
        ['MAT',25.0,40.0,'NYSE'], # matel
        ['FB',93.0,130.0,'NASDAQ'],
        ['MPC',32.0,48.0,'NYSE'],  # marathon gas refinery
        ['CHK',4.0,7.0,'NYSE'],  # cheseapeak
        ['KORS',45.0,60.0,'NYSE'], # cosmetics
        ['NGL',5.0,15.0,'NYSE'], # pipeline company
        ['CVX',78.0,100.0,'NYSE'], # chevron
        ['UA',35.0,50.0,'NYSE'], # under armour
        ['KR',35.0,50.0,'NYSE'], # kroger
        ['TGT',65.0,85.0,'NYSE'], # target. 3%
        ['CVS',80.0,120.0,'NYSE'], # CVS
        ['TFM',25.0,35.0,'NASDAQ'], # fresh market
        ['SFM',25.0,35.0,'NASDAQ'], # sprouts farms
        ['WFM',25.0,35.0,'NASDAQ'], # whole foods 1.7%        
        ['CMG',400.0,600.0,'NYSE'], # chipotle
        ['WEN',9.0,15.0,'NASDAQ'], # wendys
        ['PZZA',50.0,65.0,'NASDAQ'], # papa johns
        ['MCD',100.0,150.0,'NYSE'], # mc donalds - 3%
        ['DIN',60.0,120.0,'NYSE'], # IHOP 3.7%
        ['DENN',7.0,15.0,'NASDAQ'], # dennys - None
        ['JACK',50.0,90.0,'NASDAQ'], # jack in the box
        ['F',10.0,15.0,'NYSE'], # ford
        ['GM',25.0,40.0,'NYSE'], # GM
        ['VZ',45.0,55.0,'NYSE'], # verizon
        ['M',35.0,55.0,'NYSE'], # macy's 
        ['MMM',132.0,170.0,'NYSE'], # 3M
        ['TSO',50.0,105.0,'NYSE'], # Tesoro
        ['NTI',20.0,30.0,'NYSE'], # northern tier refinery. pays 15 % dividend
        ['INTC',25.0,34.0,'NASDAQ'], # intel 3.55% dividend
        ['BCS',5.0,15.0,'NYSE'], # intel 3.55% dividend
        ['CS',5.0,15.0,'NYSE'], # credit suisse banking stock. 6.7% dividend
        ['UBS',8.0,20.0,'NYSE'], # ubs. 6.4% dividend
        ['DB',8.0,20.0,'NYSE'], # deuchee bank.        
        ['EBAY',20.0,30.0,'NASDAQ'], # ebay
        ['UNH',100.0,140.0,'NYSE'], # united health care
        ['CI',120.0,180.0,'NYSE'], # health care. cigna
        ['PFE',25.0,38.0,'NYSE'], # pfizer 4% dividend
        ['AET',75.0,120.0,'NYSE'], # aetna 1% dividend
        ['HUM',145.0,190.0,'NYSE'], # humara 1% dividend
        ['TFX',120.0,160.0,'NYSE'], # teleflex 1% dividend. medical devices. wayne, PA
        ['LMAT',10.0,18.0,'NASDAQ'], # le maitre 1% dividend. medical devices.
        ['MSEX',23.0,40.0,'NASDAQ'], # NJ water company. 2.7% dividend
        ['WTR',30.0,40.0,'NYSE'], # PA water company
        ['AWK',60.0,93.0,'NYSE'], # canada water company
        ['AWR',20.0,53.0,'NYSE'], # american states water company
        ['PNR',20.0,53.0,'NYSE'], # pentair. partial water company that may grow
        ['DUK',70.0,100.0,'NYSE'], # DUKE energy. good electric stock. 3.8% dividend
        ['PPL',30.0,80.0,'NYSE'], # PPL comp. good electric stock. 4% dividend        
        ['XYL',40.0,75.0,'NYSE'], # water tech company
        ['DPS',85.0,105.0,'NYSE'], # dr pepper
        ['CINF',52.0,70.0,'NASDAQ'], # insurance. cincy. 3% dividend
        ['GILD',75.0,110.0,'NASDAQ'], # gilead biotech
        ['AMGN',130.0,170.0,'NASDAQ'], # biotech. california. 2.7% dividend
        ['BIIB',200.0,300.0,'NASDAQ'], # Biogen biotech. california. 0.0% dividend
        ['SLP',7.0,15.0,'NASDAQ'], # Simulations Plus. 1.8% dividend. biomedical
        ['GVP',2.0,3.0,'NYSEMKT'], # GSE nuclear, oil simulations company
        ['TAP',80.0,100.0,'NYSE'], # molson beer. 1.8% dividend
        ['RTN',115.0,160.0,'NYSE'], # ratheon. defense. 2.1% dividend
        ['VLO',45.0,70.0,'NYSE'], # oil refinery 3.9% dividend
        ['ABBV',50.0,70.0,'NYSE'], # pharma 4.0% dividend
        ['WDC',35.0,80.0,'NYSE'], # western digital 4.2% dividend
        ['STX',30.0,50.0,'NYSE'], # seagate 7% dividend
        ['BLK',200.0,500.0,'NYSE'], # black rock 2.9% dividend
        ['ADC',20.0,50.0,'NYSE'], # real estate 4.9% dividend.
        ['NTRI',10.0,30.0,'NASDAQ'], # nutrisystem 4.0% dividend.                 
        ['MET',30.0,60.0,'NYSE'], # insurance 3.8% dividend.                 
        ['WY',20.0,35.0,'NYSE'], # real estate 5.% dividend.
        ['RYN',20.0,35.0,'NYSE'], # timber 3% dividend
        ['GLD',108.0,125.0,'NYSE'], # gold 
        ['DIA',120.0,200.0,'NYSE'], # Dow jones 
        ['NDAQ',40.0,70.0,'NASDAQ'], # nasdaq trader. 1.7% dividend
        ['TSN',40.0,70.0,'NYSE'], # tyson foods. 1.% dividend        
        #['NDX',2000.0,5000.0], # nasdaq index
        ['GSK',35.0,70.0,'NYSE'], # pharma. 6.% dividend          
        ['BMY',55.0,70.0,'NYSE'], # Bristol-Myers Squibb. 6.% dividend          
        ['CRM',50.0,75.0,'NYSE'], # salesforce. cloud platform service. 0.% dividend. nielsen is using them       
        ['ADP',75.0,100.0,'NYSE'], # automatic data processing. cloud platform service. 2.% dividend. 
        ['INFY',15.0,25.0,'NYSE'], # infosys. IT/software company. 2.% dividend          
        #['TCS',2000.0,2800.0], # TCS. IT/software company. 1.7% dividend          
        ['MCK',130.0,200.0,'NYSE'], # mckessen. health care robotics and machine dosing. 0.7% dividend
        ['BHP',15.0,40.0,'NYSE'], # BHP billington. mining company with 11% dividend. steve's pick. not so sure about this one
        ['BP',20.0,45.0,'NYSE'], # british patroleum.  8.2% dividends
        ['NEE',100.0,140.0,'NYSE'], # florida electrical company.  2.7% dividends
        ['ABX',8.0,20.0,'NYSE'], #Barrick Gold mining company 0.6% dividend
        ['GG',10.0,20.0,'NYSE'], # Goldcorp mining company 1.6% dividend
        ['NEM',16.0,35.0,'NYSE'], # Newmont Mining gold mining company 0.4% dividend
        ['AUY',1.3,3.4,'NYSE'], # Yamana Gold mining company 2.5% dividend Canada
        ['NOA',1.3,4.0,'NYSE'], # Mining US. 2% dividend.         
        ['HMY',2.3,5.0,'NYSE'], # Harmony gold Mining US.
        ['GFI',3.3,6.0,'NYSE'], # Gold fields unlimited. south african gold
        ['VALE',3.3,6.0,'NYSE'], # mineral miner in brazil 2.dividend
        ['EGO',3.3,6.0,'NYSE'], # eldarado gold.
        ['BTG',1.3,4.0,'NYSEMKT'], # b2gold
        ['KGC',1.3,3.8,'NYSE'], # Kinross Gold mining company 0.0% dividend Canada
        ['CSCO',15.0,35.0,'NASDAQ'], # cisco. 3.7%
        ['KMI',10.0,40.0,'NYSE'], # kinder morgan. Berkshire hathaway is investing in them. 2.9%
        ['GNOW',0.1,2.0,'NASDAQ'], # urgent care nano cap. check carefully
        ['ENSG',10.0,25.0,'NASDAQ'], # urgent care small cap. check carefully
        ['ADPT',45.0,70.0,'NYSE'], # urgent care small cap. check carefully. no dividend
        ['EVHC',18.0,33.0,'NYSE'], # urgent care mid cap. check carefully. no dividend
        ['LPNT',60.0,80.0,'NASDAQ'], # urgent care mid cap. check carefully. no dividend
        ['THC',23.0,30.0,'NYSE'], # urgent care/intensive care mid cap. check carefully. no dividend
        ['SHAK',33.0,60.0,'NYSE'], # shake shack.
        ['UAL',45.0,70.0,'NYSE'], # united airlines
        ['DAL',30.0,50.0,'NYSE'], # delta airlines 2% dividend
        ['VOO',100.0,200.0,'NYSE'], # vanguard MUTF
        ['VFINX',100.0,200.0,'MUTF'], # vanguard MUTF
        ['VFIAX',100.0,200.0,'VFIAX'], # vanguard MUTF
        ['VPU',75.0,125.0,'NYSE'], # vanguard utilities, 3.3% dividend                
        ['RYU',50.0,100.0,'NYSE'], # equal weight utilities,
        ['VBK',50.0,170.0,'NYSE'], # vanguard small cap growth
        ['VYM',60.0,90.0,'NYSE'], # vanguard large cap mutual fund 3.1% dividend
        ['IVE',70.0,130.0,'NYSE'], # ishare mutual fund
        
        ['TSLA',200.0,300.0,'NASDAQ'], # united airlines       
        ['VA',30.0,70.0,'NASDAQ'], # virgin atlantic
        ['HOG',40.0,55.0,'NYSE'], # 3% dividend harley davidson
        ['S',2.0,5.0,'NYSE'], # sprint
        ['TMUS',2.0,5.0,'NASDAQ'], # t-mobile
        ['TWTR',10.0,20.0,'NYSE'], # twitter
        ['PIR',5.0,10.0,'NYSE'], # pier 1 imports
        ['DDD',15.0,25.0,'NYSE'], # 3D printing manufacturer
        ['XONE',10.0,15.0,'NASDAQ'], # 3D printing manufacturer exone
        ['SSYS',20.0,40.0,'NASDAQ'], # 3D printing manufacturer exone
        ['AMAT',13.0,27.0,'NASDAQ'], # chip gear manufacturer
        ['GPRO',10.0,19.0,'NASDAQ'], # go pro stock
        ['IXYS',10.0,15.0,'NASDAQ'], # parts manufacturer for drones        
        ['INVN',4.0,10.0,'NASDAQ'], # parts manufacturer for drones. motion control
        ['LMT',150.0,300.0,'NYSE'], # lockheed martin. 2.92
        ['BA',100.0,150.0,'NYSE'], # boeing. 2.92
        ['NOC',170.0,250.0,'NYSE'], # northrop gruman. 2.92
        ['STM',4.0,8.0,'NYSE'], # parts manufacturer for drones. motion control. geneva based. won apple smart watch bid
        ['MXL',16.0,30.0,'NYSE'], # semiconductor manu.
        ['NBIX',40.0,60.0,'NASDAQ'], # random bio pharma company. 0- dividend
        ['WB',20.0,60.0,'NASDAQ'], # random company
        ['NXPI',70.0,100.0,'NASDAQ'], # semi-conductor manufacturer
        ['TXN',50.0,70.0,'NASDAQ'], # texas instraments. semi-conductor manufacturer
        ['INFN',10.0,20.0,'NASDAQ'], # infera semi-conductor manufacturer.
        ['GBSN',3.0,8.0,'NASDAQ'], # genetics testing company
        ['AMAG',20.0,50.0,'NASDAQ'], # pharma in iron deficiency. high zacks rating
        ['MOH',60.0,80.0,'NYSE'], # Molina health. zach's #1
        ['CRL',70.0,100.0,'NYSE'], # Charles river health. zach's #2
        ['AIRM',30.0,50.0,'NASDAQ'], # air drop pharma. zach's #2
        ['PRXL',60.0,71.0,'NASDAQ'], # paralex medical supplies
        ['FPRX',40.0,60.0,'NASDAQ'], # therapuetics
        ['EBS',30.0,50.0,'NYSE'], # emergent bio solutions. high zacks rating
        ['FCSC',1.0,3.0,'NASDAQ'], # fibrocell. random pharma
        ['GENE',2.0,3.0,'NASDAQ'], # genetics testing company
        ['OPK',8.0,13.0,'NYSE'], # genetics testing company. is subsidiary
        ['RGLS',6.0,10.0,'NASDAQ'], # bio pharma
        ['DGX',50.0,90.0,'NYSE'], # pharma testing company
        ['ORPN',2.0,5.0,'NASDAQ'], # bio pharma
        ['VIVO',15.0,25.0,'NASDAQ'], # malaria indicator stock. Meridian
         ['XON',30.0,50.0,'NYSE'], # zika indicator stock. Intrexon
         ['INO',7.0,15.0,'NASDAQ'], # best zika indicator stock. Inovio        
         ['NLNK',15.0,25.0,'NASDAQ'], # zika indicator stock. Newlink        
         ['CERS',4.0,8.0,'NASDAQ'], # zika indicator stock. ceries        
         ['SNY',30.0,50.0,'NYSE'], # zika indicator stock. sanofi        . dividend 3.72%
         ['MDVN',40.0,80.0,'NASDAQ'], # zika indicator stock. Medivation. no dividend
         ['JCP',5.0,15.0,'NYSE'], # JC pennies.
         ['DQ',20.0,35.0,'NYSE'], # Daqo New Energy Corp. zacks rated high
         ['CAT',60.0,90.0,'NYSE'], # Catepillar, 3.8% dividend. most shorted
         ['CBA',6.0,9.0,'NYSE'], # clearbridge. energy company, 10% dividend. 
         ['UTX',80.0,120.0,'NYSE'], # united  technolgoy. most shorted, 2.4% dividend.
         ['HON',95.0,130.0,'NYSE'], # honeywell. 2%
         ['V',65.0,100.0,'NYSE'], # visa. 0.7%
         ['MO',50.0,70.0,'NYSE'], # tobacco company. Altria 3%
         ['RAI',40.0,60.0,'NYSE'], # reynolds stock. tobacco. 3%         
         ['TAP',80.0,120.0,'NYSE'], # molson-coors. 1.7%         
         ['STZ',140.0,180.0,'NYSE'], # constellation drinks stock. 1%
         ['BWLD',100.0,180.0,'NASDAQ'], # BW3's
         ['TXRH',35.0,80.0,'NASDAQ'], # texas road house
         ['CGNX',30.0,80.0,'NASDAQ'], # machine vision. 0.8%
         ['CFX',30.0,80.0,'NYSE'], # colfax?
         ['PCLN',1000.0,1500.0,'NASDAQ'], # priceline
         ['TRIP',50.0,70.0,'NASDAQ'], # trip adviser
         ['SWHC',10.0,30.0,'NASDAQ'], # smith and wessin
         ['RGR',40.0,70.0,'NYSE'], # ruger 2.5% dividend
         ['OLN',10.0,30.0,'NYSE'], # winchester++ 3% dividend
         ['TWLO',20.0,40.0,'NYSE'], # twilio
         ['BKS',7.0,15.0,'NYSE'], # barnes & nobles. 5% dividend
         ['DNKN',35.0,55.0,'NASDAQ'], # dunkin doughnuts. 2.7% dividend         
         ['SBUX',35.0,75.0,'NASDAQ'], # starbucks. 1.5% dividend         
         ['KKD',15.0,30.0,'NYSE'], # krispy kreme 
         ['JVA',4.0,10.0,'NASDAQ'], # JAVA. pure coffee holding
         ['VIAB',30.0,80.0,'NASDAQ'], # viacom 3.7% dividend
         #['NTDOY',30.0,80.0,'OTCMKTS'], # viacom 3.7% dividend  
         #['NTDOY',30.0,80.0,'OTC'], # viacom 3.7% dividend         
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
    stock_info = RequestStocks(stock_names, f)

    if Pickle:
        pickle.dump( stock_info, open( '/Users/schae/testarea/finances/googlefinance/out/stocks_%s_%s_%s.p' %(t.tm_year,t.tm_mon,t.tm_mday), "wb" ) )
        sys.exit(0)

    map_for_rsi = GetLimits()
    # process the existing information
    for i in stock_list:
        check(stock_info, f, i[0], i[1], i[2], i[3], history_stock_info, isPreMarket, map_for_rsi)
                      
    f.write('------------------------------------------\n')
    #print 'flush'
    #sys.stdout.flush()
    f.flush()
    #print 'flushed'
    #sys.stdout.flush()
    if isPreMarket:
        time.sleep(600.0) # every 10 minutes
    else:
        time.sleep(30.0)

f.close()

