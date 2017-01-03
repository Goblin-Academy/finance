from yahoo_finance import Share
import pickle
import MA_analysis as ma
import base
import sys, time
import ROOT
from array import array
WAIT=base.WAIT
out_path = base.out_path
out_file_type = base.out_file_type

#%K = 100[(C - L14)/(H14 - L14)]
#
#C = the most recent closing price
#L14 = the low of the 14 previous trading sessions
#H14 = the highest price traded during the same 14-day period.
#
#%D = 3-period moving average of %K
### Relative Strength Index
#-----------------------------------------
def GetStochastic(history, days = 14, start_date=None):
    t=ma.GetTime(start_date)
    this_date_index=None
    this_date_index_n = 0
    #print 'start_date',start_date
    if len(history)<1:
        return 0.0,0.0,0.0 #stoch,over_bought_today,over_sold_today
    
    for hindex in range(0,len(history)):
        h = history[len(history)-hindex-1]
        this_t = ma.GetTime(h['Date'])
        #print 'this: ',h['Date']
        if this_t<=t:
            this_date_index=hindex
            this_date_index_n+=1
        else:
            break
    #sys.exit(0)
    iter_days = 0
    iter_days_first=0
    last_ndays_highs = []
    last_ndays_lows = []
    my_today=0.0
    if True:
        beginning = this_date_index_n-days
        if len(history)<this_date_index_n-days:
            beginning = 1
        #print 'beginning:',beginning
        for hindex in range(beginning,len(history)):
            h = history[len(history)-hindex-1]
            #print h
            a=float(h['Close'])
            iter_days_first+=1
            if iter_days_first<days:
                last_ndays_highs+=[float(h['High'])]
                last_ndays_lows+=[float(h['Low'])]
            elif iter_days_first==days:
                last_ndays_highs+=[float(h['High'])]
                last_ndays_lows+=[float(h['Low'])]
                my_today=float(h['Close'])
                break
    #print last_ndays
    my_max = max(last_ndays_highs) 
    my_min = min(last_ndays_lows)
    stoch=0.0
    #print start_date
    #print 'my_today ',my_today,' min: ',my_min,' my_max: ',my_max
    if my_max-my_min>0.0:
        stoch = 100.0*(my_today-my_min)/(my_max-my_min)
    over_bought_today = 0.8*my_max+0.2*my_min
    #over_bought_today = (-1.0*my_min*(0.8) + my_min)/(1.-0.8)
    #over_sold_today = (my_max*0.2 + my_min)/1.2
    over_sold_today = 0.2*my_max+0.8*my_min
    #print stoch,' ',over_sold_today
    return stoch,over_bought_today,over_sold_today

### Relative Strength Index
#-----------------------------------------
def GetRSI(history, days = 14, start_date=None):
    t=ma.GetTime(start_date)
    this_date_index=None
    for hindex in range(0,len(history)):
        h = history[len(history)-hindex-1]
        this_t = ma.GetTime(h['Date'])
        if this_t<=t:
            this_date_index=hindex
        else:
            break
    list_avg_gains=[]
    list_avg_losses=[]
    avg_gain=0.0
    avg_loss=0.0
    iter_days = 0
    iter_days_first=0
    if True:
        beginning = 1
        last_close = 0.0
        if len(history)>250:
            beginning = len(history)-250
        for hindex in range(beginning,len(history)):
            h = history[len(history)-hindex-1]
            hn1 = history[len(history)-hindex]  # day before           
            #a=h['Change']
            #a=float(h['Close'])-float(h['Open'])
            last_close = float(h['Close'])
            a=float(h['Close'])-float(hn1['Close'])
            ag=0.0
            al=0.0
            if a>0.0:
                ag=a
            else:
                al=a            
            iter_days_first+=1
            if iter_days_first<days:
                if a>0.0:
                    avg_gain+=a
                else:
                    avg_loss+=a
            elif iter_days_first==days:
                avg_gain/=float(days)
                avg_loss/=float(days)
            else:
                avg_gain=(avg_gain*float(days-1) + ag)/float(days)
                avg_loss=(avg_loss*float(days-1) + al)/float(days)
            if (this_date_index-days+1)<=hindex:
                iter_days+=1
                list_avg_gains+=[avg_gain]
                list_avg_losses+=[avg_loss]
            if iter_days==days:
                break
    ag=0.0
    al=0.0
    if len(list_avg_gains)>1:
        ag = list_avg_gains[len(list_avg_gains)-1]
    if len(list_avg_losses)>1:
        al = abs(list_avg_losses[len(list_avg_losses)-1])
    rsi=50.0
    if al!=0.0:
        rsi = 100.0 - 100.0/(1.0+ag/al)
    # solve the for the upper and lower values
    #upper_ag = float(days)*0.7-avg_gain*float(days-1)
    #lower_al = float(days)*avg_loss-avg_loss*float(days-1)

    # Try these
    #rsi = 100.0 - 100.0/(1.0+ag/al)
    #agnn = (1-C)/C*al
    #agnn=(ag*float(days-1) + XX)/float(days)
    #XX = (1-C)/C*al*float(days) - ag*float(days-1)
    #avg_loss=(avg_loss*float(days-1) + XX)/float(days)
    # Gain Required
    C=(1.0-70.0/100.0)
    #ag = (1.0-C)*al/C
    #ag = (avg_gain*float(days-1) + XX)/float(days)
    #upper_ag = (1.0-C)*al/C*float(days)-avg_gain*float(days-1)
    upper_ag = (1-C)/C*al*float(days)-ag*float(days-1)
    # Loss Required
    #ag*C/(1.0-C) = alnnn
    #alnnn=(al*float(days-1) + XX)/float(days)
    #ag*C/(1.0-C)*float(days)-al*float(days-1) = ( XX)
    C=(1.0-30.0/100.0)
    #lower_al = float(days)*ag/(1.0/C-1.0)-al*float(days-1)
    lower_al = ag*C/(1.0-C)*float(days)-al*float(days-1)
    #print last_close,' ',upper_ag,' ',lower_al
    return rsi,(last_close+upper_ag),(last_close - lower_al)
                    
#-----------------------------------------
def Draw(history, days = 14, start_date=None):
    base.Style(ROOT)
    c1,pads,padScaling,ratioPadScaling = base.DoRatio(ROOT)
    
    t = ma.GetTime(start_date)

    x_axis=[]
    bins_price=[]
    bins_rsi=[]
    bins_stoch=[]
    all_rsi=[]
    all_stoch=[]
    nday=0
    ticker='N/A'
    first_date=None
    for h in history:
        this_t = ma.GetTime(h['Date'])
        if this_t<=t:
            x_axis+=[nday]
            ticker = h['Symbol']
            if first_date==None:
                first_date=h['Date']
            bins_price=[float(h['Close'])]+bins_price
            this_rsi = GetRSI(history, 14, h['Date'])
            bins_rsi = [this_rsi[0]]+bins_rsi
            all_rsi = [this_rsi]+all_rsi
            this_stoch = GetStochastic(history, 14, h['Date']) 
            bins_stoch = [this_stoch[0]]+bins_stoch
            all_stoch = [this_stoch]+all_stoch
            nday+=1
            if nday==days:
                x_axis+=[nday]
                break;
        
    # start plotting
    runArray_day = array('d',x_axis)
    hprice = ROOT.TH1F('price','price',len(runArray_day)-1,runArray_day)
    hrsi = ROOT.TH1F('rsi','rsi',len(runArray_day)-1,runArray_day)
    hprice.GetXaxis().SetTitle('Days')
    hprice.GetYaxis().SetTitle('Price for '+ticker)
    hrsi.GetYaxis().SetTitle('RSI')
    hstoch = ROOT.TH1F('stoch','stoch',len(runArray_day)-1,runArray_day)
    hstoch.GetYaxis().SetTitle('Stochastic')
    hstochma = ROOT.TH1F('stochma','stochma',len(runArray_day)-1,runArray_day)
    hstochma.GetYaxis().SetTitle('Stochastic MA')
    if start_date:
        hprice.GetXaxis().SetTitle('Days since '+start_date)

    bins_stoch_ma = ma.GetMovingAverageFromListAndReturnList(bins_stoch, 3)
    for i in range(0,len(x_axis)-1):
        hprice.SetBinContent(i+1,bins_price[i])
        hprice.SetBinError(i+1,0.0)
    #print len(bins_stoch),' for this many: ',len(x_axis)
    #print bins_stoch
    for i in range(0,len(x_axis)-1):
        hrsi.SetBinContent(i+1,bins_rsi[i])
        hrsi.SetBinError(i+1,0.0)
        hstoch.SetBinContent(i+1,bins_stoch[i])
        hstoch.SetBinError(i+1,0.0)
        hstochma.SetBinContent(i+1,bins_stoch_ma[i])
        hstochma.SetBinError(i+1,0.0)
        
    hrsi.SetLineColor(2)
    hrsi.SetMarkerColor(2)
    hrsi.GetYaxis().SetRangeUser(0.0,100.0)
    hrsi.GetYaxis().SetNdivisions(507)
    hstoch.SetLineColor(2)
    hstoch.SetMarkerColor(2)
    hstoch.GetYaxis().SetRangeUser(0.0,100.0)
    hstoch.GetYaxis().SetNdivisions(507)
    hstochma.SetLineColor(3)
    hstochma.SetMarkerColor(3)
    hstochma.GetYaxis().SetRangeUser(0.0,100.0)
    hstochma.GetYaxis().SetNdivisions(507)
    
    # Format
    base.Format([hprice],ROOT,True, padScaling,hist_name='')
    base.Format([hrsi,hstoch,hstochma],ROOT,True, ratioPadScaling,hist_name='')

    # Draw
    pads[0].cd()
    hprice.Draw('lp')

    # ratio pad
    pads[1].cd()
    l30 = ROOT.TLine(0.0,30.0,float(days),30.0)
    l50 = ROOT.TLine(0.0,50.0,float(days),50.0)
    l70 = ROOT.TLine(0.0,70.0,float(days),70.0)
    l20 = ROOT.TLine(0.0,20.0,float(days),20.0)
    l80 = ROOT.TLine(0.0,80.0,float(days),80.0)
    hrsi.Draw('lp')
    l50.SetLineWidth(2)
    l30.SetLineWidth(2)
    l70.SetLineWidth(2)
    l30.SetLineStyle(2)
    l70.SetLineStyle(2)
    l20.SetLineWidth(2)
    l80.SetLineWidth(2)
    l20.SetLineStyle(2)
    l80.SetLineStyle(2)
    l30.Draw()
    l50.Draw()
    l70.Draw()

    # ratio legend
    legr = ROOT.TLegend(0.1, 0.06, 0.4, 0.26);
    legr.SetBorderSize(0);
    legr.SetFillStyle(0);
    legr.AddEntry(hrsi, "14 day RSI");
    legr.Draw();
    
    # legend
    pads[0].cd()
    leg = ROOT.TLegend(0.18, 0.1, 0.55, 0.3);
    leg.SetBorderSize(0);
    leg.SetFillStyle(0);
    leg.AddEntry(hprice, "Closing Price");
    leg.Draw();

    # finish    
    c1.Update()
    if start_date==None:
        start_date = first_date
    c1.SaveAs(out_path+'/rsi/'+ticker+'_'+start_date+'.'+out_file_type)
    if WAIT:
        c1.WaitPrimitive()
        raw_input('waiting...')

    # draw the stochastic
    pads[1].cd()
    hstoch.Draw('lp')
    hstochma.Draw('lp same')
    l20.Draw()
    l50.Draw()
    l80.Draw()
     
    # ratio legend
    legr.Clear()
    legr.AddEntry(hstoch, "14 day Stochastic");
    legr.AddEntry(hstochma, "3 day MA of Stoch.");
    legr.Draw();
    
    # finish    
    c1.Update()
    if start_date==None:
        start_date = first_date
    c1.SaveAs(out_path+'/stoch/'+ticker+'_'+start_date+'.'+out_file_type)
    if WAIT:
        c1.WaitPrimitive()
        raw_input('waiting...')

    #print all_rsi[len(all_rsi)-1]
    return [ticker,hrsi.GetBinContent(hrsi.GetNbinsX()),
            all_rsi[len(all_rsi)-1][1], # over bought
            all_rsi[len(all_rsi)-1][2], # over sold
            hstoch.GetBinContent(hstoch.GetNbinsX()),
            all_stoch[len(all_stoch)-1][1], # over bought
            all_stoch[len(all_stoch)-1][2], # over sold 
            hstochma.GetBinContent(hstochma.GetNbinsX())]

#-----------------------------------------
def sortMe(my_list,upper=70.0, lower=30.0, TYPE='RSI', cbin=1):
    return_list_sell=[]
    return_list_buy=[]
    for m in my_list:
        if len(m)==0:
            continue
        if m[cbin]>upper:
            return_list_buy+=['OVERBUY %s %s: %0.3f' %(m[0],TYPE,m[cbin])]
        if m[cbin]<lower:
            return_list_sell+=['OVERSELL %s %s: %0.3f' %(m[0],TYPE,m[cbin])]
    return return_list_buy,return_list_sell
#-----------------------------------------
def runWithTicker(yahoo,history=None):
    if not WAIT:
        ROOT.gROOT.SetBatch(True)
    if history==None:
        history = ma.GetHistoricalData(yahoo)
    try:
        return Draw(history, 200, ma.GetToday())
    except TypeError:
        return []
    
#-----------------------------------------
def run(ticker='AMZN'):
    if not WAIT:
        ROOT.gROOT.SetBatch(True)
    
    yahoo = ma.GetShare(ticker)
    runWithTicker(yahoo)

if __name__ == "__main__":
        
    run()
