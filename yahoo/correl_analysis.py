from yahoo_finance import Share
import pickle
import MA_analysis as ma
import base
import sys, time
import ROOT
from array import array
from scipy.stats.stats import pearsonr
Pickle=False
loadPickle=False
WAIT=False
### Relative Strength Index
#-----------------------------------------
def GetCorrelation(history, ref_hist, days = 10, start_date=None):
    t=ma.GetTime(start_date)
    this_date_index=0
    for hindex in range(0,len(history)):
        h = history[len(history)-hindex-1]
        this_t = ma.GetTime(h['Date'])
        if this_t<=t:
            this_date_index=hindex
        else:
            break
    iter_days = 0
    hlist=[]
    rlist=[]
    for hindex in range(this_date_index-days,len(history)):
        h = history[len(history)-hindex-1]
        href = ref_hist[len(ref_hist)-hindex-1]

        if iter_days<days:
            hlist+=[float(h['Close'])]
            rlist+=[float(href['Close'])]
            iter_days+=1
    #print pearsonr(array('d',hlist),array('d',rlist))
    return pearsonr(hlist,rlist)[0]
                    
#-----------------------------------------
def Draw(history, ref_hist, days = 14, start_date=None):
    ma.Style()
    c1,pads,padScaling,ratioPadScaling = base.DoRatio(ROOT)
    
    t = ma.GetTime(start_date)

    x_axis=[]
    bins_price=[]
    bins_refprice=[]
    bins_correl=[]
    nday=0
    ticker='N/A'
    first_date=None
    it=0
    h1=None
    total_correl = GetCorrelation(history, ref_hist, days, start_date)
    for h in history:
        this_t = ma.GetTime(h['Date'])
        #h1={}
        #h1['Close']=float(h['Close'])
        #if it>0:
        #    h1=history[it-1]
        it+=1        
        if this_t<=t:
            if h1==None:
                h1 = history[it-1]
            x_axis+=[nday]
            ticker = h['Symbol']
            if first_date==None:
                first_date=h['Date']
            #bins_price=[(float(h1['Close'])-float(h['Close']))/float(h1['Close'])]+bins_price
            bins_price=[(float(h['Close']))]+bins_price
            bins_correl = [GetCorrelation(history, ref_hist, 10, h['Date'])]+bins_correl
            nday+=1
            if nday==days:
                x_axis+=[nday]
                break;
    nday=0
    it=0
    h1=None
    for h in ref_hist:
        this_t = ma.GetTime(h['Date'])
        #h1={}
        #h1['Close']=float(h['Close'])
        
        #if it>0:
        #    h1=ref_hist[it-1]
        it+=1
        if this_t<=t:
            if h1==None:
                h1 = ref_hist[it-1]
            
            #bins_refprice=[float(h['Close'])]+bins_refprice
            #bins_refprice=[(float(h1['Close'])-float(h['Close']))/float(h1['Close'])]+bins_refprice
            bins_refprice=[float(h['Close'])]+bins_refprice
            nday+=1
            if nday==days:
                break;

    h0=bins_refprice[0]
    for h in range(0,len(bins_refprice)):
        bins_refprice[h] = (bins_refprice[h]-h0)/h0
    h0=bins_price[0]
    for h in range(0,len(bins_price)):
        bins_price[h] = (bins_price[h]-h0)/h0
    # start plotting
    runArray_day = array('d',x_axis)
    hprice = ROOT.TH1F('price','price',len(runArray_day)-1,runArray_day)
    hrefprice = ROOT.TH1F('refprice','refprice',len(runArray_day)-1,runArray_day)
    hcorr = ROOT.TH1F('correl','correl',len(runArray_day)-1,runArray_day)
    hprice.GetXaxis().SetTitle('Days')
    hprice.GetYaxis().SetTitle('Relative Daily Change for '+ticker)
    hcorr.GetYaxis().SetTitle('Pearson Coef.')    
    if start_date:
        hprice.GetXaxis().SetTitle('Days since '+start_date)

    for i in range(0,len(x_axis)-1):
        hprice.SetBinContent(i+1,bins_price[i])
        hprice.SetBinError(i+1,0.0)        
    for i in range(0,len(x_axis)-1):
        hrefprice.SetBinContent(i+1,bins_refprice[i])
        hrefprice.SetBinError(i+1,0.0)        
    for i in range(0,len(x_axis)-1):
        hcorr.SetBinContent(i+1,bins_correl[i])
        hcorr.SetBinError(i+1,0.0)

    hrefprice.SetLineColor(2)
    hrefprice.SetMarkerColor(2)
    hcorr.SetLineColor(2)
    hcorr.SetMarkerColor(2)
    hcorr.GetYaxis().SetRangeUser(-1.0,1.0)
    hcorr.GetYaxis().SetNdivisions(507)
    
    # Format
    base.Format([hprice,hrefprice],ROOT,True, padScaling,hist_name='')
    base.Format([hcorr],ROOT,True, ratioPadScaling,hist_name='')

    # Draw
    pads[0].cd()
    hprice.Draw('lp')
    hrefprice.Draw('lp same')

    # ratio pad
    pads[1].cd()
    hcorr.Draw('lp')
    
    # ratio legend
    legr = ROOT.TLegend(0.1, 0.06, 0.4, 0.26);
    legr.SetBorderSize(0);
    legr.SetFillStyle(0);
    legr.AddEntry(hcorr, "10 day Pearson Coef.");
    legr.Draw();
    
    # legend
    pads[0].cd()
    leg = ROOT.TLegend(0.18, 0.1, 0.55, 0.3);
    leg.SetBorderSize(0);
    leg.SetFillStyle(0);
    leg.AddEntry(hprice, "Closing Price with tot. corr %0.3f" %(total_correl));
    leg.AddEntry(hrefprice, "DJIA");
    leg.Draw();

    # finish    
    c1.Update()
    if start_date==None:
        start_date = first_date
    c1.SaveAs('/Users/schae/testarea/finances/yahoo-finance/corr/'+ticker+'_'+start_date+'.pdf')
    if WAIT:
        c1.WaitPrimitive()
        raw_input('waiting...')
        
#-----------------------------------------
def runWithTicker(yahoo, reference='DIA',ref_hist=None,history=None):
    if not WAIT:
        ROOT.gROOT.SetBatch(True)
    if ref_hist==None:
        ref = ma.GetShare(reference)        
        ref_hist = ma.GetHistoricalData(ref)
    if history==None:
        history = ma.GetHistoricalData(yahoo)
    try:
        Draw(history, ref_hist, 200, ma.GetToday())
    except (TypeError, IndexError):
        return []
    
#-----------------------------------------
def run(ticker='YHOO'):
    if not WAIT:
        ROOT.gROOT.SetBatch(True)
    yahoo = ma.GetShare(ticker)
    runWithTicker(yahoo)

if __name__ == "__main__":
        
    run('GOOGL')
