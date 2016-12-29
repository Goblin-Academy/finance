from yahoo_finance import Share
import pickle
import MA_analysis as ma
import base
import sys, time
import ROOT
from array import array
Pickle=False
loadPickle=False
WAIT=False

##
##http://www.investopedia.com/terms/m/macd.asp
##What is a 'Moving Average Convergence Divergence - MACD'
##Moving average convergence divergence (MACD) is a trend-following momentum indicator that shows the relationship between two moving averages of prices. The MACD is calculated by subtracting the 26-day exponential moving average (EMA) from the 12-day EMA. A nine-day EMA of the MACD, called the "signal line", is then plotted on top of the MACD, functioning as a trigger for buy and sell signals.
##
##

#-----------------------------------------
def Draw(history, days = 50, start_date=None):
    ma.Style()
    c1,pads,padScaling,ratioPadScaling = base.DoRatio(ROOT)
    
    t = ma.GetTime(start_date)

    x_axis=[]
    bins_price=[]
    bins_macd_12day=[]
    bins_macd_26day=[]
    bins_macd_9day=[]
    bins_macd_diff=[]
    bins_macd_9diff=[]
    bins_ppo=[]     # percentage price oscillator
    bins_ppo_9ema=[]     # percentage price oscillator
    bins_ppo_signal=[]     # signal line
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
            nineday = ma.GetExpMovingAverage(history, 9, h['Date'])
            twelveday = ma.GetExpMovingAverage(history, 12, h['Date'])
            twentysixday = ma.GetExpMovingAverage(history, 26, h['Date'])
            bins_macd_9day =[nineday]+bins_macd_9day
            bins_macd_12day =[twelveday]+bins_macd_12day
            bins_macd_26day=[twentysixday]+bins_macd_26day
            bins_macd_diff=[twelveday-twentysixday]+bins_macd_diff
            if twentysixday>0.0:
                bins_ppo=[100.0*(twelveday-twentysixday)/twentysixday]+bins_ppo
            else:
                bins_ppo=[0.0]+bins_ppo
                
            nday+=1
            if nday==days:
                x_axis+=[nday]
                break;
    for m in range(0,len(bins_macd_diff)):
        bins_macd_9diff+=[ ma.GetExpMovingAverageFromList(bins_macd_diff,9,m)]
    for m in range(0,len(bins_ppo)):
        bins_ppo_9ema+=[ ma.GetExpMovingAverageFromList(bins_ppo,9,m)]
        
    # start plotting
    runArray_day = array('d',x_axis)
    hprice = ROOT.TH1F('price','price',len(runArray_day)-1,runArray_day)
    hmacd9day = ROOT.TH1F('macd9day','macd9day',len(runArray_day)-1,runArray_day)
    hmacd12day = ROOT.TH1F('macd12day','macd12day',len(runArray_day)-1,runArray_day)
    hmacd26day = ROOT.TH1F('macd26day','macd26day',len(runArray_day)-1,runArray_day)
    hmacddiff = ROOT.TH1F('macddiff','macddiff',len(runArray_day)-1,runArray_day)
    hmacd9diff = ROOT.TH1F('macd9diff','macd9diff',len(runArray_day)-1,runArray_day)
    hppo = ROOT.TH1F('ppo','ppo',len(runArray_day)-1,runArray_day)    
    hppo9dayema = ROOT.TH1F('ppo9dayema','ppo9dayema',len(runArray_day)-1,runArray_day)
    hdiff = ROOT.TH1F('diff','diff',len(runArray_day)-1,runArray_day)
    hdiffppo = ROOT.TH1F('diffppo','diffppo',len(runArray_day)-1,runArray_day) 
    hprice.GetXaxis().SetTitle('Days')
    hprice.GetYaxis().SetTitle('Price for '+ticker)
    if start_date:
        hprice.GetXaxis().SetTitle('Days since '+start_date)
        hmacddiff.GetXaxis().SetTitle('Days since '+start_date)
        hmacddiff.GetYaxis().SetTitle('MACD')        
        hppo.GetYaxis().SetTitle('PPO')        
        hppo.GetXaxis().SetTitle('Days since '+start_date)        

    for i in range(0,len(x_axis)-1):
        hprice.SetBinContent(i+1,bins_price[i])
        hprice.SetBinError(i+1,0.0)        
    for i in range(0,len(x_axis)-1):
        hmacd9day.SetBinContent(i+1,bins_macd_9day[i])
        hmacd9day.SetBinError(i+1,0.0)
    for i in range(0,len(x_axis)-1):
        hmacd12day.SetBinContent(i+1,bins_macd_12day[i])
        hmacd12day.SetBinError(i+1,0.0)        
    for i in range(0,len(x_axis)-1):
        hmacddiff.SetBinContent(i+1,bins_macd_diff[i])
        hmacddiff.SetBinError(i+1,0.0)        
    for i in range(0,len(x_axis)-1):
        hmacd9diff.SetBinContent(i+1,bins_macd_9diff[i])
        hmacd9diff.SetBinError(i+1,0.0)        
    for i in range(0,len(x_axis)-1):
        hdiff.SetBinContent(i+1,bins_macd_diff[i]-bins_macd_9diff[i])
        hdiff.SetBinError(i+1,0.0)        
    for i in range(0,len(x_axis)-1):
        hdiffppo.SetBinContent(i+1,bins_ppo[i]-bins_ppo_9ema[i])
        hdiffppo.SetBinError(i+1,0.0)        
    for i in range(0,len(x_axis)-1):
        hmacd26day.SetBinContent(i+1,bins_macd_26day[i])
        hmacd26day.SetBinError(i+1,0.0)        
    for i in range(0,len(x_axis)-1):
        hppo.SetBinContent(i+1,bins_ppo[i])
        hppo.SetBinError(i+1,0.0)        
    for i in range(0,len(x_axis)-1):
        hppo9dayema.SetBinContent(i+1,bins_ppo_9ema[i])
        hppo9dayema.SetBinError(i+1,0.0)        

    hmacd9day.SetLineColor(2)
    hmacd9day.SetMarkerColor(2)
    hmacd12day.SetLineColor(3)
    hmacd12day.SetMarkerColor(3)
    hmacd26day.SetLineColor(4)
    hmacd26day.SetMarkerColor(4)
    hmacddiff.SetLineColor(1)
    hmacddiff.SetMarkerColor(1)
    hmacd9diff.SetLineColor(2)
    hmacd9diff.SetMarkerColor(2)
    hppo.SetLineColor(4)
    hppo.SetMarkerColor(4)
    hppo9dayema.SetLineColor(5)
    hppo9dayema.SetMarkerColor(5)
    hdiffppo.SetLineColor(6)
    hdiffppo.SetMarkerColor(6)
    hdiffppo.SetFillColor(6)    
    hdiffppo.SetFillStyle(1001)
    hdiff.SetLineColor(3)
    hdiff.SetMarkerColor(3)    
    hdiff.SetFillColor(3)
    hdiff.SetFillStyle(1001)    

    # Format
    base.Format([hprice,hmacd9day,hmacd12day,hmacd26day],ROOT,True, padScaling,hist_name='')
    base.Format([hmacddiff,hmacd9diff,hdiff,hppo,hppo9dayema,hdiffppo],ROOT,True, ratioPadScaling,hist_name='')

    # Draw
    pads[0].cd()
    hprice.Draw('lp')
    hmacd9day.Draw('lpsame')
    hmacd12day.Draw('lpsame')
    hmacd26day.Draw('lpsame')
    # ratio pad
    pads[1].cd()
    hmacddiff.Draw('lp')
    hdiff.Draw("HIST same")
    hmacddiff.Draw('lp same')    
    hmacd9diff.Draw('lpsame')
    #hppo.Draw('lpsame')        
    #hppo9dayema.Draw('lpsame')        
    #hdiffppo.Draw('lpsame')        

    # ratio legend
    legr = ROOT.TLegend(0.1, 0.06, 0.4, 0.26);
    legr.SetBorderSize(0);
    legr.SetFillStyle(0);
    legr.AddEntry(hmacddiff, "12 Day MACD");
    #legr.AddEntry(hmacd9diff, "9 Day MACD");
    legr.AddEntry(hmacd9diff, "Signal Line");
    legr.AddEntry(hdiff, "Diff");
    #legr.AddEntry(hppo, "PPO");
    #legr.AddEntry(hppo9dayema, "PPO Signal Line");
    #legr.AddEntry(hdiffppo, "PPO Indicator");
    legr.Draw();
    
    # legend
    pads[0].cd()
    leg = ROOT.TLegend(0.18, 0.1, 0.55, 0.3);
    leg.SetBorderSize(0);
    leg.SetFillStyle(0);
    leg.AddEntry(hprice, "Closing Price");
    leg.AddEntry(hmacd9day, "9 Day ExpMA");
    leg.AddEntry(hmacd12day, "12 Day ExpMA");
    leg.AddEntry(hmacd26day, "26 Day ExpMA");
    leg.Draw();

    #decision_100day,decision_ndays_100days = AnalyzeMA(bins_ma_100day, bins_ma_20day)
    #decision_50day,decision_ndays_50days = AnalyzeMA(bins_ma_50day, bins_ma_20day)
    
    # finish    
    c1.Update()
    if start_date==None:
        start_date = first_date
    c1.SaveAs('/Users/schae/testarea/finances/yahoo-finance/macd/'+ticker+'_'+start_date+'.pdf')
    if WAIT:
        c1.WaitPrimitive()
        raw_input('waiting...')

    my_buy_date = -999
    my_sell_date = -999
    for a in range(0,hdiff.GetNbinsX()):
        if hdiff.GetBinContent(hdiff.GetNbinsX()-a)>0.0 and hdiff.GetBinContent(hdiff.GetNbinsX()-a-1)<0.0 and my_buy_date<0.0:
            my_buy_date=a
        if hdiff.GetBinContent(hdiff.GetNbinsX()-a)<0.0 and hdiff.GetBinContent(hdiff.GetNbinsX()-a-1)>0.0 and my_sell_date<0.0:
            my_sell_date=a
        
    return [ticker,my_buy_date,my_sell_date,hdiff.GetBinContent(hdiff.GetNbinsX())]

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
def run(ticker='YHOO'):
    if not WAIT:
        ROOT.gROOT.SetBatch(True)
    
    yahoo = ma.GetShare(ticker)
    runWithTicker(yahoo)
    #history = ma.GetHistoricalData(yahoo)
    #h=history[0]
    #print 'Moving: ',ma.GetAverage(history, 20, h['Date'])
    #print 'exponential: ',ma.GetExpMovingAverage(history, 20, h['Date'])    
    #Draw(history, 200, ma.GetToday())

if __name__ == "__main__":
        
    run()
