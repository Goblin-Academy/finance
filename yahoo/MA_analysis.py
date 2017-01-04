from yahoo_finance import Share
import yahoo_finance
import httplib
import pickle
import sys, time, datetime
import ROOT
import base
import socket
import urllib2
from array import array
Pickle=False
loadPickle=False
WAIT=base.WAIT

out_path = base.out_path
out_file_type = base.out_file_type
#-----------------------------------------    
def GetShare(ticker='YHOO'):
    return Share(ticker)

#-----------------------------------------
def BasicData(yahoo):
    print yahoo.get_open()
    #'36.60'
    print yahoo.get_price()
    #'36.84'
    print yahoo.get_trade_datetime()
    #'2014-02-05 20:50:00 UTC+0000'
#-----------------------------------------
def GetHistoricalData(yahoo, start_date=None): #'2016-02-07'

    if start_date==None:
        start_date = base.GetToday()
    history_stocks_info = None 
    #print history_stocks_info
    if Pickle:
        pickle.dump( history_stocks_info, open( out_path+'/out/stocks_%s.p' %(yahoo._key), "wb" ) )
        sys.exit(0)
    elif loadPickle:
        history_stocks_info = pickle.load( open( out_path+"/out/stocks_%s.p" %(yahoo._key), "rb" ) )
    else:
        while history_stocks_info==None:
            try:
                history_stocks_info = yahoo.get_historical('2014-06-07', start_date)
            except (socket.gaierror, socket.error, httplib.BadStatusLine, yahoo_finance.YQLResponseMalformedError, urllib2.HTTPError):
                print 'socket.gaierror...retrying in 5s'
                sys.stdout.flush()
                history_stocks_info=None
                time.sleep(30.0)
    return history_stocks_info

#---------------
def GetStdDev(istart, days = 20, multiple=2.0, ma_list=[], start_date=None):
    #t=base.GetTime(start_date)

    #avg=0.0
    #iter_days = 0
    #print 'ma_list: ',ma_list
    tmp_list=ma_list[:len(ma_list)-istart]
    if len(ma_list)-istart>days:
        tmp_list=ma_list[len(ma_list)-istart-days:len(ma_list)-istart]
        #print tmp_list
    if len(tmp_list)<2:
        tmp_list=[0.0,0.0]
    #print base.pstdev(tmp_list)
    #print tmp_list
    return base.pstdev(tmp_list)*multiple

#---------------
def GetAverage(history, days = 50, start_date=None):
    t=base.GetTime(start_date)
    line=[]
    avg=0.0
    iter_days = 0
    for h in history:
        this_t = base.GetTime(h['Date'])
        if this_t<=t:
            iter_days+=1
            avg+=float(h['Close'])
            if days==20:
                line+=[h['Close']]
        if iter_days==days:
            break
    if iter_days>0.0:
        avg /= iter_days
    #if days==20:
    #    print line
    #    print avg
    return avg

#---------------
def GetMovingAverageFromListAndReturnList(my_list, days = 9):
    ma_list=[]
    for i in range(0,len(my_list)):
        ma_list+=[GetMovingAverageFromList(my_list,days,i)]
    return ma_list
#---------------
def GetMovingAverageFromList(my_list, days = 9, start_point=0):

    ndays=0
    ma=0.0
    if start_point-days+1<0:
        return my_list[0]
    #print 'start_point: ',start_point
    for m in range(start_point-days+1,len(my_list)):
        ma+=my_list[m]
        #print '   ',my_list[m],' m: ',m
        ndays+=1
        if ndays==days:
            break
    if days>0.0:
        ma /= float(days)
    return ma

#---------------
def GetExpMovingAverageFromList(my_list, days = 9, start_point=0):

    prev_ema=None
    k = 2.0 / (days + 1.0);
    ndays=0
    for m in range(start_point-days+1,len(my_list)):
        if start_point-days>-0.5:
            if prev_ema==None:
                prev_ema=my_list[m]
            else: #EMA = Price(t) * k + EMA(y) * (1-k)
                prev_ema=(my_list[m]-prev_ema)*k + prev_ema
            ndays+=1
        if ndays==days:
            #print m,' start: ',start_point,' len: ',len(my_list)
            break
    if prev_ema==None:
        return 0.0
    return prev_ema

#---------------
def GetExpMovingAverage(history, days = 50, start_date=None):
    t=base.GetTime(start_date)
    k = 2.0 / (days + 1.0);
    #tod = datetime.datetime.now()
    #d = datetime.timedelta(days = days)
    #tdt = datetime.datetime.fromtimestamp(time.mktime(t))
    #a = tdt - d
    #print 'AAA: ',a
    #avg=0.0
    iter_days = 0
    prev_ema=-1.0
    #print 'Start and today: ',start_date
    this_date_index = 0
    for hindex in range(0,len(history)):
        h = history[len(history)-hindex-1]
        this_t = base.GetTime(h['Date'])
        #this_ttd = datetime.datetime.fromtimestamp(time.mktime(this_t))
        if this_t<=t:
            this_date_index=hindex
        else:
            break
    #print this_date_index,' days ',days
    if (this_date_index-days+1)>=0:
        #print this_date_index-days+1,' ',len(history)
        for hindex in range(this_date_index-days+1,len(history)):
            h = history[len(history)-hindex-1]
            this_t = base.GetTime(h['Date'])
            if this_t<=t:
                iter_days+=1
                if prev_ema<0.0:
                    prev_ema=float(h['Close'])
                else: #EMA = Price(t) * k + EMA(y) * (1-k)
                    prev_ema=(float(h['Close'])-prev_ema)*k + prev_ema
            #print h['Date'],' ',h['Close'],' ',prev_ema
            if iter_days==days:
                break
    return prev_ema

#----------------
def AnalyzeMA(long_ma, short_ma):
    for i in range(1,len(long_ma)-1):
        # search backward from the current date.
        j = len(long_ma)-i
        if short_ma[j]<=long_ma[j] and short_ma[j-1]>=long_ma[j-1]:
            print 'time to sell was ',i,' days ago.'
            return 'sell',i
        elif short_ma[j]>=long_ma[j] and short_ma[j-1]<=long_ma[j-1]:
            print 'time to buy was ',i,' days ago.'
            return 'buy',i
    return 'N/A',1000

#----------------
def Draw(history, days = 50, start_date=None):
    base.Style(ROOT)
    c1 = ROOT.TCanvas("c1","stocks",50,50,600,600);
    t = base.GetTime(start_date)

    Nbolganger=2.0
    NbolgangerMA=20
    
    x_axis=[]
    x_e_axis=[]
    bins_price=[]
    bins_price_for_stddev=[]    
    bins_eh_price=[]
    bins_el_price=[]
    bins_ma_50day=[]
    bins_ma_20day=[]
    bins_ma_bol=[]
    bins_ma_bolsigma=[]        
    bins_ma_100day=[]
    bins_ma_200day=[]
    nday=0
    ticker='N/A'
    first_date=None
    for h in history:
        this_t = base.GetTime(h['Date'])
        if this_t<=t:
            if (nday)<(days):
                x_axis+=[nday]
                x_e_axis+=[0.0]
            ticker = h['Symbol']
            if first_date==None:
                first_date=h['Date']
            bins_ma_bol =[GetAverage(history, NbolgangerMA, h['Date'])]+bins_ma_bol
            bins_price_for_stddev=[float(h['Close'])]+bins_price
            if (nday)<(days):
                bins_price=[float(h['Close'])]+bins_price
                bins_eh_price=[float(h['High'])-float(h['Close'])]+bins_eh_price
                bins_el_price=[float(h['Close'])-float(h['Low'])]+bins_el_price
                bins_ma_20day =[GetAverage(history, 20, h['Date'])]+bins_ma_20day                
                bins_ma_50day =[GetAverage(history, 50, h['Date'])]+bins_ma_50day
                bins_ma_100day=[GetAverage(history, 100, h['Date'])]+bins_ma_100day
                bins_ma_200day=[GetAverage(history, 200, h['Date'])]+bins_ma_200day
            nday+=1
            if nday==days:
                x_axis+=[nday]
            if (nday)==(days+NbolgangerMA):
                break;
    #print len(bins_ma_bol)
    #print len(x_axis)
    #print len(bins_ma_20day)    
    for i in range(0,len(bins_ma_bol)-NbolgangerMA):        
        bins_ma_bolsigma =[GetStdDev(i, NbolgangerMA, Nbolganger, bins_price_for_stddev, h['Date'])]+bins_ma_bolsigma
    #print len(bins_ma_bolsigma)
    # start plotting
    if len(bins_price)>0:
        #bins_price+=[bins_price[0]]
        bins_price=[bins_price[0]]+bins_price
    #print bins_price
    #print x_axis[1:len(x_axis)]
    runArray_day = array('d',x_axis)
    runArray_e_day = array('d',x_e_axis)
    runArray_price = array('d',bins_price)
    #print len(runArray_price)
    #print len(x_axis)
    runArray_el_price =  array('d',bins_el_price)
    runArray_eh_price =  array('d',bins_eh_price)
    if len(runArray_day)==0:
        return []
    #hprice = ROOT.TH1F('price','price',len(runArray_day)-1,runArray_day)
    hprice = ROOT.TGraphAsymmErrors(len(x_axis),runArray_day,runArray_price,
                                    runArray_e_day,
                                    runArray_e_day,runArray_el_price,runArray_eh_price)
    hbolbandsize = ROOT.TH1F('bolbandsize','bolbandsize',len(runArray_day)-1,runArray_day)
    hbolbandup = ROOT.TH1F('bolbandup','bolbandup',len(runArray_day)-1,runArray_day)
    hbolma = ROOT.TH1F('bolma','bolma',len(runArray_day)-1,runArray_day)
    hbolpercentb = ROOT.TH1F('bolpercentb','bolpercentb',len(runArray_day)-1,runArray_day)
    hbolbanddw = ROOT.TH1F('bolbanddw','bolbanddw',len(runArray_day)-1,runArray_day)            
    hma20day = ROOT.TH1F('ma20day','ma20day',len(runArray_day)-1,runArray_day)
    hma50day = ROOT.TH1F('ma50day','ma50day',len(runArray_day)-1,runArray_day)
    hma100day = ROOT.TH1F('ma100day','ma100day',len(runArray_day)-1,runArray_day)
    hma200day = ROOT.TH1F('ma200day','ma200day',len(runArray_day)-1,runArray_day)
    hprice.GetXaxis().SetTitle('Days')
    hprice.GetYaxis().SetTitle('Price for '+ticker)
    max_yrange = max(bins_price)
    min_yrange = min(bins_price)
    hprice.GetYaxis().SetRangeUser(min_yrange*0.93,max_yrange*1.07)
        
    if start_date:
        hprice.GetXaxis().SetTitle('Days since '+start_date)

    #for i in range(0,len(x_axis)-1):
    #    hprice.SetBinContent(i+1,bins_price[i])
    #print bins_ma_bolsigma
    #print bins_ma_bol
    ashift = len(bins_ma_bol)-len(x_axis)+1
    for i in range(0,len(x_axis)-1):
        itmp=i
        #print 'bol:',i+1,(ashift+itmp),bins_ma_bol[ashift+itmp],len(bins_ma_bol)        
        #print bins_ma_bol[ashift+itmp],bins_ma_bolsigma[itmp]
        hbolbanddw.SetBinContent(i+1,bins_ma_bol[ashift+itmp]-bins_ma_bolsigma[itmp])
        hbolbandup.SetBinContent(i+1,bins_ma_bol[ashift+itmp]+bins_ma_bolsigma[itmp])
        hbolma.SetBinError(i+1,0.0)
        hbolbandup.SetBinError(i+1,0.0)
        hbolbandsize.SetBinError(i+1,0.0)
        hbolpercentb.SetBinError(i+1,0.0)
        hbolbanddw.SetBinError(i+1,0.0)
        hbolma.SetBinContent(i+1,bins_ma_bol[ashift+itmp])
        
        if bins_ma_bol[itmp]>0.0:
            hbolbandsize.SetBinContent(i+1,2.0*bins_ma_bolsigma[itmp]/bins_ma_bol[itmp])
        if bins_ma_bolsigma[itmp]>0.0:
            hbolpercentb.SetBinContent(i+1,(bins_price[itmp]-bins_ma_bol[itmp]-bins_ma_bolsigma[itmp])/(4.0*bins_ma_bolsigma[itmp]))            
    for i in range(0,len(x_axis)-1):
        hma20day.SetBinContent(i+1,bins_ma_20day[i])
    for i in range(0,len(x_axis)-1):
        hma50day.SetBinContent(i+1,bins_ma_50day[i])
    for i in range(0,len(x_axis)-1):
        hma200day.SetBinContent(i+1,bins_ma_200day[i])
    for i in range(0,len(x_axis)-1):
        hma100day.SetBinContent(i+1,bins_ma_100day[i])        

    hma20day.SetLineColor(2)
    hma20day.SetMarkerColor(2)
    hbolbandsize.SetLineColor(2)
    hbolbandsize.SetMarkerColor(2)    
    hma50day.SetLineColor(3)
    hma50day.SetMarkerColor(3)
    hma100day.SetLineColor(4)
    hma100day.SetMarkerColor(4)
    hma200day.SetLineColor(6)
    hma200day.SetMarkerColor(6)

    hprice.SetLineColor(1)
    hprice.SetFillColor(0)
    hprice.GetXaxis().SetRangeUser(0,float(days))
    hprice.Draw()
    hprice.Draw('same lp e2')
    hma20day.Draw('lpsame')
    hma50day.Draw('lpsame')
    hma100day.Draw('lpsame')
    hma200day.Draw('lpsame')

    # legend
    leg = ROOT.TLegend(0.45, 0.2, 0.85, 0.4);
    leg.SetBorderSize(0);
    leg.SetFillStyle(0);
    leg.AddEntry(hprice, "Closing Price");
    leg.AddEntry(hma20day, "20 Day MA");
    leg.AddEntry(hma50day, "50 Day MA");
    leg.AddEntry(hma100day, "100 Day MA");
    leg.AddEntry(hma200day, "200 Day MA");
    leg.Draw();

    decision_100day,decision_ndays_100days = AnalyzeMA(bins_ma_100day, bins_ma_20day)
    decision_50day,decision_ndays_50days = AnalyzeMA(bins_ma_50day, bins_ma_20day)
    
    # finish    
    c1.Update()
    if start_date==None:
        start_date = first_date
    c1.SaveAs(out_path+'/ma/'+ticker+'_'+start_date+'.'+out_file_type)
    if WAIT:
        c1.WaitPrimitive()
        raw_input('waiting...')
    # bolanger band size
    del c1
    c1,pads,padScaling,ratioPadScaling = base.DoRatio(ROOT)
    # Format
    base.Format([hprice,hbolbandup,hbolbanddw,hbolma],ROOT,True, padScaling,hist_name='')
    base.Format([hbolbandsize,hbolpercentb],ROOT,True, ratioPadScaling,hist_name='')    
    hbolbandsize.GetXaxis().SetTitle('Days since '+start_date)
    hbolpercentb.GetXaxis().SetTitle('Days since '+start_date)
    hbolbandsize.GetYaxis().SetTitle('Bolanger Band Size')
    hbolpercentb.GetYaxis().SetTitle('Percent b')
    hprice.GetXaxis().SetRangeUser(0,float(days))
    hbolbandup.SetLineColor(3)
    hbolbandup.SetMarkerColor(3)
    hbolma.SetLineColor(2)
    hbolma.SetMarkerColor(2)
    hbolma.SetLineStyle(2)
    hbolbandup.SetLineStyle(1)
    hbolbanddw.SetLineStyle(1)
    hbolbanddw.SetLineColor(4)
    hbolbanddw.SetMarkerColor(4)
    pads[0].cd()
    hprice.Draw()
    hprice.Draw('lp same e2')
    hbolma.Draw('same')
    hbolbandup.Draw('same')
    hbolbanddw.Draw('same')
    #hbolbandsize.Draw()
    leg.Clear()
    leg.AddEntry(hbolma,'%s MA' %(NbolgangerMA))
    leg.AddEntry(hbolbandup,'Bolanger Band')
    leg.Draw()
    pads[1].cd()
    hbolpercentb.SetLineColor(2)
    hbolpercentb.SetMarkerColor(2)
    hbolbandsize.SetLineColor(3)
    hbolbandsize.SetMarkerColor(3)

    hbolbandsize.Scale(5.0)
    hbolpercentb.Draw()
    hbolbandsize.Draw('same')
    leg.Clear()
    leg.AddEntry(hbolpercentb,'Percent b' )
    leg.AddEntry(hbolbandsize,'5*Bolanger Band Size')
    leg.SetY1(0.4)
    leg.SetY2(0.6)
    leg.Draw()
    
    
    c1.Update()
    if start_date==None:
        start_date = first_date
    new_ticker = ticker.replace('^','_')
    c1.SaveAs(out_path+'/ma/'+new_ticker+'_'+start_date+'bol.'+out_file_type)
    if WAIT:
        c1.WaitPrimitive()
        raw_input('waiting...')
    return [[decision_100day,decision_ndays_100days],
            [decision_50day,decision_ndays_50days],
            bins_ma_20day[len(bins_ma_20day)-1],
            bins_ma_50day[len(bins_ma_50day)-1],
            bins_ma_100day[len(bins_ma_100day)-1],
            bins_ma_200day[len(bins_ma_200day)-1]]

#-----------------------------------------
def runWithTicker(yahoo, history=None):
    if not WAIT:
        ROOT.gROOT.SetBatch(True)
    #BasicData(yahoo)
    #print 'Get History'
    if history==None:
        history = GetHistoricalData(yahoo)
    #print 'compute 50 day average'
    #avg_50day = GetAverage(history, 50, '2016-01-15')
    #avg_20day = GetAverage(history, 20, '2016-01-15')
    #avg_200day = GetAverage(history, 200, '2016-01-15')
    #return Draw(history, 200, '2016-02-17')
    return Draw(history, 200, base.GetToday()),history
    #print 'Done'        
#-----------------------------------------
def run(ticker='TFM'):
    if not WAIT:
        ROOT.gROOT.SetBatch(True)
    
    yahoo = GetShare(ticker)
    runWithTicker(yahoo)
    
if __name__ == "__main__":
        
    run()
