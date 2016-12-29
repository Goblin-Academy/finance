import math

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
    root.gROOT.LoadMacro('plotting_scripts/atlasstyle/AtlasStyle.C')
    root.gROOT.LoadMacro('plotting_scripts/atlasstyle/AtlasUtils.C')
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
