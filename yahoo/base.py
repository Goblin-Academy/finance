import math
import sys
import time
WAIT=False
style_path = '/Users/schae/testarea/CAFAna/HWWMVACode'
out_path = '/Users/schae/testarea/finances/yahoo-finance'

html_path = '/var/www/html/finance/plot_html'

style_path = '/home/doug'
out_path = '/home/doug/testarea/finance/yahoo-finance'
out_path_www = '/var/www/html/finance/plot_html'
out_file_type = 'png'
#------------------
def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data)/float(n) # in Python 2 use sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def pstdev(data):
    """Calculates the population standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    #print n,ss,data
    pvar = ss/float(n) # the population variance
    return pvar**0.5

#-----------------------------------------  
def GenerateToys(fsec, hbg, ntoys, m_rand, root):

    if ntoys<0:
        return
    
    params=[]
    initial_params=[]    
    # Load initial params
    for par in range(0,fsec.GetNumberFreeParameters()):
        params+=[fsec.GetParameter(par)]
        initial_params+=[fsec.GetParameter(par)]
    hbg_central=[]
    hbg_error=[]    
    hbg_bin_edge=[]
    for ibin in range(0,hbg.GetNbinsX()):
        hbg_central+=[hbg.GetBinContent(ibin)]
        hbg_error+=[0.0]
        hbg_bin_edge+=[(hbg.GetXaxis().GetBinUpEdge(ibin)-hbg.GetXaxis().GetBinLowEdge(ibin))/2.0+hbg.GetXaxis().GetBinLowEdge(ibin)]

    # Run
    for i in range(0,ntoys):
        if (i%1000)==0:
            print 'Running Uncertainties for toy: ',i
        
        # smear params and set
        for par in range(0,fsec.GetNumberFreeParameters()):
            params[par]=m_rand.Gaus(initial_params[par], fsec.GetParError(par))
            fsec.SetParameter(par, root.Double(params[par]))
        # Get difference with fit
        for ibin in range(0,hbg.GetNbinsX()):
            hbg_error[ibin]+=(hbg_central[ibin]-fsec.Eval(hbg_bin_edge[ibin]))**2

    # finish
    for ibin in range(0,hbg.GetNbinsX()):
        hbg.SetBinError(ibin,math.sqrt(hbg_error[ibin]/float(ntoys)))

    # Reset
    for par in range(0,fsec.GetNumberFreeParameters()):
        fsec.SetParameter(par,initial_params[par])
def DoRatio(ROOT):
    c1 = ROOT.TCanvas("c1","stocks",50,50,600,600);
    DORATIO=True
    padScaling=1.0
    ratioPadScaling=1.0
    pads=[]
    if DORATIO:
        #print 'doing ratio'
        # CAF setup
        ratioPadRatio  = 0.3;
        markerSize = 1;
        lineWidth = 2;
        markerStyle = 20;
        scale=1.05
        padScaling      = 0.75 / (1. - ratioPadRatio) *scale;
        ratioPadScaling = 0.75*(1. / ratioPadRatio) *scale;  
        ROOT.gStyle.SetPadTopMargin(0.065);
        ROOT.gStyle.SetPadRightMargin(0.05);
        ROOT.gStyle.SetPadBottomMargin(0.16);
        ROOT.gStyle.SetPadLeftMargin(0.16);
        ROOT.gStyle.SetTitleXOffset(1.0);
        pads=[]
        pads.append( ROOT.TPad('pad0','pad0', 0.0, ratioPadRatio, 1.0, 1.0) )
        pads.append( ROOT.TPad('pad1','pad1', 0.0, 0.0, 1.0, ratioPadRatio+0.012) )
        
        pads[0].SetTopMargin(padScaling * pads[0].GetTopMargin());
        pads[0].SetBottomMargin(.015);
        pads[0].SetTickx(True);
        pads[0].SetTicky(True);
        pads[1].SetTopMargin(.015);
        #pads[1].SetBottomMargin(ratioPadScaling *pads[1].GetBottomMargin());
        #print 'margin:',ratioPadScaling *pads[1].GetBottomMargin()
        pads[1].SetBottomMargin(ratioPadScaling *pads[1].GetBottomMargin()*0.93);    
        pads[1].SetGridy(True);
        pads[1].SetTickx(True);
        pads[1].SetTicky(True);
        pads[0].Draw()
        pads[1].Draw()
        pads[0].cd()
        #base.Format([h,htada],ROOT,True, padScaling,hist_name='')
    return c1,pads,padScaling,ratioPadScaling

#---------------
def GetToday():
    t = time.localtime()
    mon = '%s' %t.tm_mon
    day = '%s' %t.tm_mday
    if t.tm_mon<10:
        mon = '0%s' %t.tm_mon
    if t.tm_mday<10:
        day = '0%s' %t.tm_mday
    start_date = '%s-%s-%s' %(t.tm_year, mon, day)
    return start_date

#---------------
def GetTime(start_date=None):
    t=None
    if start_date==None:
        t = time.localtime()
        mon = '%s' %t.tm_mon
        day = '%s' %t.tm_mday
        if t.tm_mon<10:
            mon = '0%s' %t.tm_mon
        if t.tm_mday<10:
            day = '0%s' %t.tm_mday
        start_date = '%s-%s-%s' %(t.tm_year, mon, day)
    else:
        t = time.strptime(start_date, "%Y-%m-%d")
    return t

#---------------
def GetTimeStr(start_date=None):
    t=None
    if start_date==None:
        t = time.localtime()
        mon = '%s' %t.tm_mon
        day = '%s' %t.tm_mday
        if t.tm_mon<10:
            mon = '0%s' %t.tm_mon
        if t.tm_mday<10:
            day = '0%s' %t.tm_mday
        t = '%s-%s-%s' %(t.tm_year, mon, day)
    else:
        try:
            t = time.strptime(start_date, "%Y-%m-%d")
        except:
            mon = '%s' %start_date.tm_mon
            day = '%s' %start_date.tm_mday
            if start_date.tm_mon<10:
                mon = '0%s' %start_date.tm_mon
            if start_date.tm_mday<10:
                day = '0%s' %start_date.tm_mday
            t = '%s-%s-%s' %(start_date.tm_year, mon, day)
    return t

#-----------------------------------------  
def SeperationPower(h1o, h2o):
    h1 = h1o.Clone()
    h2 = h2o.Clone()
    if h1.Integral()>0.0:
        h1.Scale(1.0/h1.Integral())
    if h2.Integral()>0.0:
        h2.Scale(1.0/h2.Integral())
    tot_sep = 0.0
    for i in range(1,h1.GetNbinsX()+1):
        #for j in range(1,h2.GetNbinsX()+1):
        bin_sum = h1.GetBinContent(i)+h2.GetBinContent(i)
        sep = 0.5*(h1.GetBinContent(i)-h2.GetBinContent(i))**2
        if bin_sum>0.0:
            sep /= bin_sum
        tot_sep += sep
            
    return tot_sep

#---------------
def Round(n,number_after_period=3):
    if n==0.0 or abs(n)<1.0e-10:
        return n
    log_n=0
    try:
        log_n = round(abs(math.log(abs(n),10)),0)
    except:
        print 'ERROR with math log on ',n
        log_n=0
    n_new = n*(10.0**(-log_n))
    n_new2 = round(n_new,number_after_period)
    
    return n_new2*(10.0**(log_n))

#---------------
def RoundScientific(n,numbers=3):
    if n==0.0 or abs(n)<1.0e-10:
        return n
    log_n=0
    try:
        log_n = round(abs(math.log(n,10)),0)
    except:
        print 'ERROR with math log on ',n
        log_n=0
    n_new = n*(10.0**(-log_n))
    if n_new<1.0:
        n_new*=10.0
        log_n-=1    
    n_new2 = round(n_new,numbers)
    return '%0.2fx10^{%0.0f}' %(n_new2,log_n)
    #return n_new2*(10.0**(log_n))

#---------------
def RoundStr(n,number_after_period=3):
    n = Round(n,number_after_period=3)
    s = '%s' %n
    if (len(s)-s.find('\.'))>(number_after_period+1):
        s = '%0.3f' %n

    return s

#-----------------------------------------  
def Style(root):
    sys.stdout.flush()
    if not hasattr(root,'SetAtlasStyle'):
        root.gROOT.LoadMacro(style_path+'/atlasstyle-00-03-05/AtlasStyle.C')
        root.gROOT.LoadMacro(style_path+'/atlasstyle-00-03-05/AtlasUtils.C')
        root.SetAtlasStyle()

#-----------------------------------------
def Format(mcs, ROOT, isData=False, ratioPadScaling=1.0, hist_name=''):

    for m in mcs:

        if m==None or not m:
            continue
        
        if ratioPadScaling!=1.0:
            m.SetMarkerSize(0.4)
            bx = m.GetXaxis();
            by = m.GetYaxis();
            bx.SetTitleSize(ROOT.gStyle.GetTitleSize("x") * ratioPadScaling);
            bx.SetLabelSize(ROOT.gStyle.GetLabelSize("x") * ratioPadScaling);
            by.SetTitleSize(ROOT.gStyle.GetTitleSize("y") * ratioPadScaling);
            by.SetTitleOffset(ROOT.gStyle.GetTitleOffset("y") / ratioPadScaling  );

            if hist_name.count('_recoilrms'):
                bx.SetTitleOffset(ROOT.gStyle.GetTitleOffset("x") *0.96  );
            else:
                bx.SetTitleOffset(ROOT.gStyle.GetTitleOffset("x") *1.19  );
            by.SetLabelSize(ROOT.gStyle.GetLabelSize("y") * ratioPadScaling);
            bx.SetLabelColor(1);
            bx.SetTickLength(bx.GetTickLength() * ratioPadScaling);

        if True: # stack underflow and overflow
            try:
                a0=m.GetBinContent(0)
                e0=m.GetBinError(0)
                e1=m.GetBinError(0)
                m.SetBinContent(1,a0+m.GetBinContent(1))
                m.SetBinError(1, math.sqrt(e0**2+e1**2))
                m.SetBinContent(0,0.0)
                m.SetBinError(0,0.0)
                last_bin = m.GetNbinsX()
                m.SetBinContent(last_bin,m.GetBinContent(last_bin)+m.GetBinContent(1+last_bin))
                m.SetBinError(last_bin,math.sqrt(m.GetBinError(last_bin)**2+m.GetBinError(1+last_bin)**2))
                m.SetBinContent(last_bin+1,0.0)
                m.SetBinError(last_bin+1,0.0)

            except AttributeError:
                pass

            
#-------------------------------------------------------------------------                                                                                                                                    
def getATLASLabels(pad, x, y, ROOT, text='', padScaling=1.0, lumi=1.4):

    l = ROOT.TLatex(x, y, 'ATLAS')
    l.SetNDC()
    l.SetTextFont(72)
    l.SetTextSize(0.055*padScaling)
    l.SetTextAlign(11)
    l.SetTextColor(ROOT.kBlack)
    l.Draw()

    delx = 0.05*pad.GetWh()/(pad.GetWw())
    labs = [l]

    if True:
        p = ROOT.TLatex(x+0.15, y, 'Internal')
        p.SetNDC()
        p.SetTextFont(42)
        p.SetTextSize(0.055*padScaling)
        p.SetTextAlign(11)
        p.SetTextColor(ROOT.kBlack)
        p.Draw()
        labs += [p]

        a = ROOT.TLatex(x, y-0.045*padScaling, '#sqrt{s} = 13 TeV Simulation')        
        if text.count('Data'):
            a = ROOT.TLatex(x, y-0.045*padScaling, '#sqrt{s} = 13 TeV, L = %.1f fb^{-1}' %(lumi))
        a.SetNDC()
        a.SetTextFont(42)
        a.SetTextSize(0.04*padScaling)
        a.SetTextAlign(12)
        a.SetTextColor(ROOT.kBlack)
        a.Draw()
        labs += [a]

    if text!='':
        c = ROOT.TLatex(x, y-0.1*padScaling, text)
        c.SetNDC()
        c.SetTextFont(42)
        c.SetTextSize(0.04*padScaling)
        c.SetTextAlign(12)
        c.SetTextColor(ROOT.kBlack)
        c.Draw()
        labs += [c]

    return labs


def getLabels(pad, x, y, ROOT, text='', padScaling=1.0):

    labs=[]
    c = ROOT.TLatex(x, y-0.13*padScaling, text)
    c.SetNDC()
    c.SetTextFont(42)
    c.SetTextSize(0.04*padScaling)
    c.SetTextAlign(12)
    c.SetTextColor(ROOT.kBlack)
    c.Draw()
    labs += [c]
    return labs

#---------------------------------------------------------------------
# Make logger object
#
def getLog(name, level = 'INFO', debug=False):

    import logging
    import sys
    
    f = logging.Formatter("Py:%(name)s: %(levelname)s - %(message)s")
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(f)
    
    log = logging.getLogger(name)
    log.addHandler(h)

    if debug:
        log.setLevel(logging.DEBUG)
    else:
        if level == 'DEBUG':   log.setLevel(logging.DEBUG)
        if level == 'INFO':    log.setLevel(logging.INFO)
        if level == 'WARNING': log.setLevel(logging.WARNING)    
        if level == 'ERROR':   log.setLevel(logging.ERROR)

    return log

#-------------------------------------------------------------------------
# Common command line option parser
#
def getParser():
    
    from optparse import OptionParser
    
    p = OptionParser(usage='usage: <path:ROOT file directory>', version='0.1')

    #
    # Options for plotEvent.py
    #
    p.add_option('-n','--nevent',  type='int',    dest='nevent',         default=0,         help='number of events')
    p.add_option('--ntoys',  type='int',    dest='ntoys',         default=-1,         help='number of toys for systematics varying fit uncertainties')    
    p.add_option('-i','--input',  type='string',    dest='input',         default=None,         help='Files to fit in a comma separated list')
    #p.add_option('-s','--sample',  type='string',    dest='data',         default='data',         help='sample')        
    p.add_option('--hname',     type='string',    dest='hname',         default=None,         help='Histogram name')
    p.add_option('--fit-dir',   type='string',    dest='fit_dir',      default='fitfuncs',         help='Fit function directory')
    p.add_option('--fit-name',  type='string',    dest='fit_name',    default='FourParamFit',         help='Fit Function name from fitfunc.py')
    p.add_option('--fit-opt',   type='string',    dest='fit_opt',    default='M',         help='Fit Function name from fitfunc.py')
    p.add_option('--add-lumi-dir',   type='string',    dest='add_lumi_dir',    default=None,         help='Add lumi dir')        

    p.add_option('--xmin',      type='float',    dest='xmin',         default=1100.0,         help='Fit range min')    
    p.add_option('--xmax',      type='float',    dest='xmax',         default=6100.0,         help='Fit range max')    
    p.add_option('--xmin-fit',  type='float',    dest='xmin_fit',         default=3570.0,         help='Fit range to exclude min')    
    p.add_option('--xmax-fit',  type='float',    dest='xmax_fit',         default=3990.0,         help='Fit range to exclude max')    
    p.add_option('--lumi',      type='float',    dest='lumi',         default=1.6,         help='Luminosity')
    p.add_option('--scale-by-lumi',      type='float',    dest='scale_by_lumi',         default=None,         help='Scale data and bkg by lumi')
    p.add_option('--scale-by-toys',      type='int',    dest='scale_by_toys',         default=1,         help='Scale data and bkg by lumi')    
    p.add_option('--scale-by-lumi-sig',      type='float',    dest='scale_by_lumi_sig',         default=None,         help='Scale data and sig by lumi')            

    p.add_option('--wait',        action='store_true', default=False,    dest='wait',     help='wait on plots')
    p.add_option('--overlay-fits',        action='store_true', default=False,    dest='overlay_fits',     help='overlay-fits')    
    p.add_option('--tada',        action='store_true', default=False,    dest='tada',     help='tada')    
    p.add_option('--fit-mc',      action='store_true', default=False,    dest='fit_mc',     help='Fit MC shape')
    p.add_option('--fit-mc-only', action='store_true', default=False,    dest='fit_mc_only',     help='Fit MC shape only')        
    p.add_option('--do-ratio',    action='store_false',default=True,     dest='do_ratio', help='do ratio plot')    
    
    return p

#-------------------------------------------------------------------------
# stock list
#
stock_list = [
        # Check stocks
        ['GOOGL',640.0,805.0], # google
        ['AMZN',450.0,700.0], # amazon
        ['AAPL',86.0,110.0], # apple
        ['MAT',25.0,40.0], # matel
        ['FB',93.0,130.0],
        ['X',20.0,55.0,'NYSE'],  # steel industry
        ['SCCO',20.0,55.0,'NYSE'],  # copper company 0.5%
        ['SPR',20.0,105.0,'NYSE'],  # spirit airlines 0.7%
        ['SFLY',20.0,105.0,'NASDAQ'],  # spirit airlines 0.7%
        ['MPC',30.0,48.0],  # marathon gas refinery
        ['WNR',25.0,80.0,'NYSE'],  # western refinery 4.% dividend.
        ['CHK',4.0,7.0],  # cheseapeak
        ['KORS',45.0,60.0], # cosmetics
        ['NGL',5.0,15.0], # pipeline company
        ['CVX',78.0,100.0], # chevron
        ['UAA',35.0,50.0], # under armour
        ['KR',35.0,50.0], # kroger. 1%
        ['SKT',25.0,50.0,'NYSE'], # tanger, 3.5% dividend  
        ['TGT',65.0,85.0], # target. 3%        
        ['CVS',80.0,120.0], # CVS 1.6%
        #['TFM',25.0,35.0], # fresh market
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
        ['AMT',45.0,155.0,'NYSE'], # connection tower company. 2.2% dividend
        ['M',35.0,55.0], # macy's
        ['TUES',1.0,55.0,'NASDAQ'], # tuesday morning corp
        ['SXI',1.0,155.0,'NYSE'], # standex
        ['MMM',132.0,170.0], # 3M
        ['TSO',50.0,105.0], # Tesoro
    #['NTI',20.0,30.0], # northern tier refinery. pays 15 % dividend
        ['INTC',25.0,34.0], # intel 3.55% dividend
        ['NVDA',25.0,234.0,'NASDAQ'], # nvidia 0.55% dividend    
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
        ['TAP',80.0,120.0], # molson beer. 1.8% dividend
        ['RTN',115.0,160.0,'NYSE'], # ratheon. defense. 2.1% dividend
        ['GD',150.0,300.0,'NYSE'], # general dynamics corp. 1.6%
        ['GE',15.0,300.0,'NYSE'], # general dynamics corp. 3.2%
        ['CXW',15.0,300.0,'NYSE'], # corecivics. jailing. 5.8% dividend
        ['GEO',15.0,300.0,'NYSE'], # geo group. jailing service florida. 6.4%
        ['SID',1.0,5.0,'NYSE'], # steel in brazil
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
        ['ANDE',40.0,70.0,'NASDAQ'], # andersons fertilzer comp. 1.7% dividend    
        ['GSK',35.0,70.0], # pharma. 6.% dividend          
        ['BMY',55.0,70.0], # Bristol-Myers Squibb. 2.75% dividend
        ['LOW',55.0,100.0,'NYSE'], # LOWES 2.% dividend
        ['HD',85.0,180.0,'NYSE'], # Home depot 2.% dividend     
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

        #['SHAK',33.0,60.0], # shake shack.
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
    #['TAP',80.0,120.0], # molson-coors. 1.7%         
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
    #['KKD',15.0,30.0,'NYSE'], # krispy kreme 
         ['JVA',4.0,10.0,'NASDAQ'], # JAVA. pure coffee holding
         ['VIAB',30.0,80.0,'NASDAQ'], # viacom 3.7% dividend

         ['^DJI',17.0e3,22.0e3,'NYSE'], # DJIA
         ['XTN',30.0,80.0,'NYSE'], # S&P transport
         ['DJTA',7.0e3,10.0e3,'NYSE'], # DJIA transport
         ['CSX',20.0,60.0,'NASDAQ'], # Train manufacture. 1.6%
         ['SB',1.0,2.0,'NYSE'], # safe builder. 2.0% 
         ['VIOO',60.0,150.0,'NYSE'], # small cap
         ['MDY',200.0,300.0,'NYSE'], # mid cap
         ['GS',150.0,300.0,'NYSE'], # Goldman saks. 1% dividend
            ['FAF',20.0,70.0,'NYSE'], # investment. 3.5.% dividend        
         ['JPM',65.0,120.0,'NYSE'], # JPM chase. 2% dividend
         ['PNC',90.0,150.0,'NYSE'], # PNC bank. 2% dividend
         ['VGT',90.0,150.0,'NYSEARCA'], # Vanguard information tech. 1.4% dividend
    ['^RUT',900.0,1500.0,'INDEXRUSSELL'], # russel 2000
    ['^RUA',900.0,1500.0,'INDEXRUSSELL'], # russel 3000
    ['^RUI',900.0,1500.0,'INDEXRUSSELL'], # russel 1000 growth index
    ['IWS',30.0,500.0,'NYSEARCA'], # russel 2000. 1.7% dividend
    ['IWM',30.0,500.0,'NYSEARCA'], # russel midcaps. 2.3% dividend
    ['IWO',30.0,500.0,'NYSEARCA'], # russel 2000 growth index. 1.2% dividend
    ['IWN',30.0,500.0,'NYSEARCA'], # russel 2000 value index. 2.3% dividend
    ['IWB',30.0,500.0,'NYSEARCA'], # russel 1000 index. 2.4% dividend
    ['IWL',30.0,500.0,'NYSEARCA'], # russel top 200 1.88% dividend
    ['IWF',30.0,500.0,'NYSEARCA'], # russel 1000 growth index. 1.8% dividend
    ['^VIX',0.0,20.0,'INDEXCBOE'], # Volatility Index. look for a point where the price is 10 points from the MA. spikes indicate fear

         #['NTDOY',30.0,80.0,'OTCMKTS'], # viacom 3.7% dividend         
        #['SPY',60.0,90.0], # spyder large cap mutual fund
        #['VIG',60.0,90.0], # vanguard large cap mutual fund 3.1% dividend
        #['WTI',20.0,35.0], # west texas intermediate. crude oil
        #['NDX',2000.0,5000.0], # nasdaq index  
        ]
