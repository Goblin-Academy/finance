from yahoo_finance import Share
import pickle
import MA_analysis as ma
import base
import sys, time
import ROOT
from array import array
Pickle=False
loadPickle=False
WAIT=base.WAIT
out_path = base.out_path
out_file_type = base.out_file_type

#-----------------------------------------
def GetVolatility(history, days = 22, start_date=None):
    bins_price=[]
    bins_rsi=[]
    nday=0
    ticker='N/A'
    first_date=None
    t = base.GetTime(start_date)
    for h in history:
        this_t = base.GetTime(h['Date'])
        if this_t<=t:
            ticker = h['Symbol']
            if first_date==None:
                first_date=h['Date']
            bins_price=[float(h['Close'])]+bins_price
            nday+=1
            if nday==days:
                break;
    # std deviation
    return base.pstdev(bins_price)

#-----------------------------------------
def GetChaikin(history, days = 20, start_date=None):
    bins_price=[]
    bins_rsi=[]
    nday=0
    ticker='N/A'
    first_date=None
    t = base.GetTime(start_date)
    chaikin=0.0
    vol=0.0
    for h in history:
        #print h
        this_t = base.GetTime(h['Date'])
        if this_t<=t:
            ticker = h['Symbol']
            if first_date==None:
                first_date=h['Date']
            mult=((float(h['Close'])-float(h['Low'])) - (float(h['High'])-float(h['Close'])))
            if (float(h['High'])-float(h['Low']))!=0.0:
                mult /=(float(h['High'])-float(h['Low']))
            chaikin+=mult*float(h['Volume'])
            vol+=float(h['Volume'])
            nday+=1
            if nday==days:
                break;
    # std deviation
    if vol==0.0:
        vol=1.0
    return chaikin/vol

### Relative Strength Index
#-----------------------------------------
def Draw(history, days = 14, start_date=None, isVolume=0):
    base.Style(ROOT)
    c1,pads,padScaling,ratioPadScaling = base.DoRatio(ROOT)
    
    t = base.GetTime(start_date)

    x_axis=[]
    x_e_axis=[]
    bins_price=[]
    bins_eh_price=[]    
    bins_el_price=[]    
    bins_rsi=[]
    bins_volt=[]
    bins_chaikin=[]    
    nday=0
    ticker='N/A'
    first_date=None
    hindex=0
    for h in history:
        this_t = base.GetTime(h['Date'])
        if this_t<=t:
            if nday>0:
                x_axis+=[float(nday)]
            x_e_axis+=[0.0]
            ticker = h['Symbol']
            if first_date==None:
                first_date=h['Date']
            bins_price=[float(h['Close'])]+bins_price
            bins_eh_price=[float(h['High'])-float(h['Close'])]+bins_eh_price
            bins_el_price=[float(h['Close'])-float(h['Low'])]+bins_el_price
            bins_volt=[GetVolatility(history,22,h['Date'])]+bins_volt
            bins_chaikin=[GetChaikin(history,20,h['Date'])]+bins_chaikin
                
            a=0.0
            if hindex>0:
                hn1 = history[len(history)-hindex]                
                a=float(h['Close'])-float(hn1['Close'])
            #bins_rsi = [ float(h['Volume'])]+bins_rsi
            if a>0.0:
                bins_rsi = [ float(h['Volume'])]+bins_rsi
            else:
                bins_rsi = [ -1.0*float(h['Volume'])]+bins_rsi
                
            nday+=1
            if nday==days:
                x_axis+=[float(nday)]
                break;
            hindex+=1
        
    # start plotting
    #print x_axis
    #print bins_price
    #print 'np: ',len(bins_price),' ',len(x_axis)
    runArray_day = array('d',x_axis)
    runArray_price = array('d',bins_price)
    runArray_e_day = array('d',x_e_axis)
    runArray_el_price = array('d',bins_el_price)
    runArray_eh_price = array('d',bins_eh_price)
    #hprice = ROOT.TH1F('price','price',len(runArray_day)-1,runArray_day)
    hprice = ROOT.TGraphAsymmErrors(len(x_axis),runArray_day,runArray_price,
                                    runArray_e_day,
                                    runArray_e_day,runArray_el_price,runArray_eh_price)
    hprice.SetName('price')
    hrsi = ROOT.TH1F('volume','volume',len(runArray_day)-1,runArray_day)
    hvolt = ROOT.TH1F('volatility','volatility',len(runArray_day)-1,runArray_day)
    hchaikin = ROOT.TH1F('chaikin','chaikin',len(runArray_day)-1,runArray_day)
    hprice.GetXaxis().SetTitle('Days')
    hvolt.GetXaxis().SetTitle('Days')
    hrsi.GetXaxis().SetTitle('Days')
    hchaikin.GetXaxis().SetTitle('Days')
    hprice.GetYaxis().SetTitle('Price for '+ticker)
    hrsi.GetYaxis().SetTitle('Volume')    
    hvolt.GetYaxis().SetTitle('Volatility')
    hchaikin.GetYaxis().SetTitle('CMF')
    if start_date:
        hprice.GetXaxis().SetTitle('Days since '+start_date)

    #for i in range(0,len(x_axis)-1):
    #    hprice.SetBinContent(i+1,bins_price[i])
    #    hprice.SetBinError(i+1,0.0)        
    for i in range(0,len(x_axis)-1):
        hrsi.SetBinContent(i+1,bins_rsi[i])
        hrsi.SetBinError(i+1,0.0)
    for i in range(0,len(x_axis)-1):
        hvolt.SetBinContent(i+1,bins_volt[i])
        hvolt.SetBinError(i+1,0.0)
    for i in range(0,len(x_axis)-1):
        hchaikin.SetBinContent(i+1,bins_chaikin[i])
        hchaikin.SetBinError(i+1,0.0)

    hrsi.SetLineColor(2)
    hrsi.SetMarkerColor(2)
    hvolt.SetLineColor(3)
    hvolt.SetMarkerColor(3)
    hchaikin.SetLineColor(4)
    hchaikin.SetMarkerColor(4)
    #hrsi.GetYaxis().SetRangeUser(0.0,100.0)
    hrsi.GetYaxis().SetNdivisions(507)
    hvolt.GetYaxis().SetNdivisions(507)
    hchaikin.GetYaxis().SetNdivisions(507)
    
    # Format
    base.Format([hprice],ROOT,True, padScaling,hist_name='')
    base.Format([hrsi,hvolt,hchaikin],ROOT,True, ratioPadScaling,hist_name='')

    # Draw
    pads[0].cd()
    hprice.SetLineColor(2)
    hprice.SetFillColor(0)
    hprice.GetXaxis().SetRangeUser(0.0,x_axis[len(x_axis)-1])
    #hprice.Draw('lp')
    hprice.Draw()
    hprice.Draw('same pl e2')    

    # ratio pad
    pads[1].cd()
    #l30 = ROOT.TLine(0.0,30.0,float(days),30.0)
    #l50 = ROOT.TLine(0.0,50.0,float(days),50.0)
    #l70 = ROOT.TLine(0.0,70.0,float(days),70.0)
    if isVolume==0:
        hrsi.Draw('lp')
    elif isVolume==1:
        hvolt.Draw('lp ')
    elif isVolume==2:
        hchaikin.Draw('lp ')
        l05 = ROOT.TLine(0.0,0.05,float(days),0.05)
        l05.SetLineWidth(2)
        l05.SetLineColor(3)
        l05.SetLineStyle(2)
        l05.Draw()
        m05 = ROOT.TLine(0.0,-0.05,float(days),-0.05)
        m05.SetLineWidth(2)
        m05.SetLineColor(2)
        m05.SetLineStyle(2)
        m05.Draw()

    # ratio legend
    legr = ROOT.TLegend(0.1, 0.06, 0.4, 0.26);
    legr.SetBorderSize(0);
    legr.SetFillStyle(0);
    if isVolume==0:
        legr.AddEntry(hrsi, "Volume");
    elif isVolume==1:
        legr.AddEntry(hvolt, "Volatility");
    elif isVolume==2:
        legr.AddEntry(hchaikin, "CMF");            
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
    if isVolume==0:
        c1.SaveAs(out_path+'/obv/'+ticker+'_'+start_date+'.'+out_file_type)
    elif isVolume==1:
        c1.SaveAs(out_path+'/obv/'+ticker+'_'+start_date+'volt.'+out_file_type)
    elif isVolume==2:
        c1.SaveAs(out_path+'/obv/'+ticker+'_'+start_date+'chaikin.'+out_file_type)
    if WAIT:
        c1.WaitPrimitive()
        raw_input('waiting...')
        
#-----------------------------------------
def runWithTicker(yahoo, history=None):
    if not WAIT:
        ROOT.gROOT.SetBatch(True)
    if history==None:
        history = ma.GetHistoricalData(yahoo)
    try:
        Draw(history, 200, ma.GetToday(), isVolume=1)
        Draw(history, 200, ma.GetToday(), isVolume=0)
        Draw(history, 200, ma.GetToday(), isVolume=2)
    except TypeError:
        return []
    
#-----------------------------------------
def run(ticker='GOOGL'):
    if not WAIT:
        ROOT.gROOT.SetBatch(True)
    
    yahoo = ma.GetShare(ticker)
    runWithTicker(yahoo)

if __name__ == "__main__":
        
    run()
