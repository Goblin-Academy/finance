// ElliotEngineView.cpp : implementation of the CElliotEngineView class
//

#include "stdafx.h"
#include <math.h>
#pragma warning (disable: 4786)
#include <map>
#include "chartdir.h"
#include "ElliotEngine.h"

#include "ElliotEngineDoc.h"
#include "ElliotEngineView.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CElliotEngineView

IMPLEMENT_DYNCREATE(CElliotEngineView, CFormView)

BEGIN_MESSAGE_MAP(CElliotEngineView, CFormView)
	//{{AFX_MSG_MAP(CElliotEngineView)
	ON_WM_SIZE()
	ON_BN_CLICKED(IDC_LOGSCALE, OnSelectChange)
	ON_EN_KILLFOCUS(IDC_MOVAVG1, OnTextChange)
	ON_CBN_SELCHANGE(IDC_CHARTSIZE, OnSelchangeChartsize)
	ON_WM_HSCROLL()
	ON_WM_MOUSEMOVE()
	ON_BN_CLICKED(IDC_MAJORVGRID, OnSelectChange)
	ON_CBN_SELCHANGE(IDC_CHARTTYPE, OnSelectChange)
	ON_EN_KILLFOCUS(IDC_MOVAVG2, OnTextChange)
	ON_BN_CLICKED(IDC_VOLUME, OnSelectChange)
	ON_BN_CLICKED(IDC_MINORVGRID, OnSelectChange)
	ON_CBN_SELCHANGE(IDC_INDICATOR4, OnSelectChange)
	ON_CBN_SELCHANGE(IDC_INDICATOR3, OnSelectChange)
	ON_CBN_SELCHANGE(IDC_INDICATOR2, OnSelectChange)
	ON_CBN_SELCHANGE(IDC_INDICATOR1, OnSelectChange)
	ON_BN_CLICKED(IDC_HGRID, OnSelectChange)
	ON_CBN_SELCHANGE(IDC_BAND, OnSelectChange)
	ON_CBN_SELCHANGE(IDC_AVGTYPE2, OnSelectChange)
	ON_CBN_SELCHANGE(IDC_AVGTYPE1, OnSelectChange)
	ON_BN_CLICKED(IDC_MONOWAVES, OnSelectChange)
	ON_CBN_SELCHANGE(IDC_TIMERANGE, OnResolutionChange)
	//}}AFX_MSG_MAP
	// Standard printing commands
	ON_COMMAND(ID_FILE_PRINT, CFormView::OnFilePrint)
	ON_COMMAND(ID_FILE_PRINT_DIRECT, CFormView::OnFilePrint)
	ON_COMMAND(ID_FILE_PRINT_PREVIEW, CFormView::OnFilePrintPreview)
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CElliotEngineView construction/destruction

CElliotEngineView::CElliotEngineView()
	: CFormView(CElliotEngineView::IDD)
{
	//{{AFX_DATA_INIT(CElliotEngineView)
	//}}AFX_DATA_INIT
	m_noOfPoints = 0;
	m_timeStamps = 0;
	m_openData = 0;
	m_closeData = 0;
	m_highData = 0;
	m_lowData = 0;
	m_volData = 0;
}

CElliotEngineView::~CElliotEngineView()
{
	delete[] m_timeStamps;
	delete[] m_openData;
	delete[] m_closeData;
	delete[] m_highData;
	delete[] m_lowData;
	delete[] m_volData;
}

void CElliotEngineView::DoDataExchange(CDataExchange* pDX)
{
	CFormView::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CElliotEngineView)
	DDX_Control(pDX, IDC_MONOWAVES, m_ShowMonowaves);
	DDX_Control(pDX, IDC_CHARTSCROLLBAR, m_ChartScrollBar);
	DDX_Control(pDX, IDC_WAVESCROLL, m_WaveScroll);
	DDX_Control(pDX, IDC_MOVAVG2, m_MovAvg2);
	DDX_Control(pDX, IDC_MOVAVG1, m_MovAvg1);
	DDX_Control(pDX, IDC_MINORVGRID, m_MinorVGrid);
	DDX_Control(pDX, IDC_MAJORVGRID, m_MajorVGrid);
	DDX_Control(pDX, IDC_LOGSCALE, m_LogScale);
	DDX_Control(pDX, IDC_HGRID, m_HGrid);
	DDX_Control(pDX, IDC_VOLUME, m_Volume);
	DDX_Control(pDX, IDC_INDICATOR4, m_Indicator4);
	DDX_Control(pDX, IDC_INDICATOR3, m_Indicator3);
	DDX_Control(pDX, IDC_INDICATOR2, m_Indicator2);
	DDX_Control(pDX, IDC_INDICATOR1, m_Indicator1);
	DDX_Control(pDX, IDC_CHARTTYPE, m_ChartType);
	DDX_Control(pDX, IDC_CHARTSIZE, m_ChartSize);
	DDX_Control(pDX, IDC_BAND, m_Band);
	DDX_Control(pDX, IDC_AVGTYPE2, m_AvgType2);
	DDX_Control(pDX, IDC_AVGTYPE1, m_AvgType1);
	DDX_Control(pDX, IDC_TIMERANGE, m_TimeRange);
	DDX_Control(pDX, IDC_STATIC_CHART, m_Chart);
	//}}AFX_DATA_MAP
}

BOOL CElliotEngineView::PreCreateWindow(CREATESTRUCT& cs)
{
	// TODO: Modify the Window class or styles here by modifying
	//  the CREATESTRUCT cs

	return CFormView::PreCreateWindow(cs);
}


static const TCHAR *timeRanges[] = 
{
	_T("1"), _T("1 day"),
	_T("2"), _T("2 days"),
	_T("5"), _T("5 days"),
	_T("10"), _T("10 days"),
	_T("30"), _T("1 month"),
	_T("90"), _T("3 months"),
	_T("180"), _T("6 months"),
	_T("360"), _T("1 year"),
	_T("720"), _T("2 years"),
	_T("1800"), _T("5 years"),
	_T("3600"), _T("10 years"),
	_T("36000"), _T("100 years")
};


static const TCHAR *chartSizes[] =
{
	_T("S"), _T("Small"),
	_T("M"), _T("Medium"),
	_T("L"), _T("Large"),
	_T("H"), _T("Huge")
};


static const TCHAR *chartTypes[] =
{
	_T("None"), _T("None"),
	_T("CandleStick"), _T("CandleStick"),
	_T("Close"), _T("Closing Price"),
	_T("Median"), _T("Median Price"),
	_T("OHLC"), _T("OHLC"),
	_T("TP"), _T("Typical Price"),
	_T("WC"), _T("Weighted Close")
};


static const TCHAR *bandTypes[] =
{
	_T("None"), _T("None"),
	_T("BB"), _T("Bollinger Band"),
	_T("DC"), _T("Donchain Channel"),
	_T("Envelop"), _T("Envelop (SMA 20 +/- 10%)")
};


static const TCHAR *avgTypes[] =
{
	_T("None"), _T("None"),
	_T("SMA"), _T("Simple"),
	_T("EMA"), _T("Exponential"),
	_T("TMA"), _T("Triangular"),
	_T("WMA"), _T("Weighted")
};


static const TCHAR *indicatorTypes[] =
{
	_T("None"), _T("None"),
	_T("AccDist"), _T("Accumulation/Distribution"),
	_T("AroonOsc"), _T("Aroon Oscillator"),
	_T("Aroon"), _T("Aroon Up/Down"),
	_T("ADX"), _T("Avg Directional Index"),
	_T("ATR"), _T("Avg True Range"),
	_T("BBW"), _T("Bollinger Band Width"),
	_T("CMF"), _T("Chaikin Money Flow"),
	_T("COscillator"), _T("Chaikin Oscillator"),
	_T("CVolatility"), _T("Chaikin Volatility"),
	_T("CLV"), _T("Close Location Value"),
	_T("CCI"), _T("Commodity Channel Index"),
	_T("DPO"), _T("Detrended Price Osc"),
	_T("DCW"), _T("Donchian Channel Width"),
	_T("EMV"), _T("Ease of Movement"),
	_T("FStoch"), _T("Fast Stochastic"),
	_T("MACD"), _T("MACD"),
	_T("MDX"), _T("Mass Index"),
	_T("Momentum"), _T("Momentum"),
	_T("MFI"), _T("Money Flow Index"),
	_T("NVI"), _T("Neg Volume Index"),
	_T("OBV"), _T("On Balance Volume"),
	_T("Performance"), _T("Performance"),
	_T("PPO"), _T("% Price Oscillator"),
	_T("PVO"), _T("% Volume Oscillator"),
	_T("PVI"), _T("Pos Volume Index"),
	_T("PVT"), _T("Price Volume Trend"),
	_T("ROC"), _T("Rate of Change"),
	_T("RSI"), _T("RSI"),
	_T("SStoch"), _T("Slow Stochastic"),
	_T("StochRSI"), _T("StochRSI"),
	_T("TRIX"), _T("TRIX"),
	_T("UO"), _T("Ultimate Oscillator"),
	_T("Vol"), _T("Volume"),
	_T("WilliamR"), _T("William's %R")
};

//
// Helper utility to initialize a combo box from an array of text
//
static void initComboBox(CComboBox &b, const TCHAR *list[], int count, const TCHAR *initial)
{
	b.Clear();
	for (int i = 0; i < count; i += 2)
		//The odd index are the display text, the even index are the keys
		b.SetItemDataPtr(b.AddString(list[i + 1]), (void *)(list[i]));
	b.SelectString(0, initial);
}

ETime ChartDirectorDate2ETime(double d)
{
  int YMD = Chart::getChartYMD(d);
  int s = (int)((__int64)d % DAYSECONDS);
  ETime n;
  n.Change(YMD / 10000, (YMD / 100) % 100, YMD % 100, s / 3600, (s / 60) % 60, s % 60);
  return n;
}


void CElliotEngineView::OnInitialUpdate()
{
	CFormView::OnInitialUpdate();
	ResizeParentToFit();

	//
	// Intialialize the controls
	//
	initComboBox(m_TimeRange, timeRanges, sizeof(timeRanges) / sizeof(*timeRanges), _T("3 months"));
	initComboBox(m_ChartSize, chartSizes, sizeof(chartSizes) / sizeof(*chartSizes), _T("Large"));
	initComboBox(m_ChartType, chartTypes, sizeof(chartTypes) / sizeof(*chartTypes), _T("Closing Price"));
	initComboBox(m_Band, bandTypes, sizeof(bandTypes) / sizeof(*bandTypes), _T("None"));
	initComboBox(m_AvgType1, avgTypes, sizeof(avgTypes) / sizeof(*avgTypes), _T("None"));
	initComboBox(m_AvgType2, avgTypes, sizeof(avgTypes) / sizeof(*avgTypes), _T("None"));
	initComboBox(m_Indicator1, indicatorTypes, sizeof(indicatorTypes) / sizeof(*indicatorTypes), _T("RSI"));
	initComboBox(m_Indicator2, indicatorTypes, sizeof(indicatorTypes) / sizeof(*indicatorTypes), _T("None"));
	initComboBox(m_Indicator3, indicatorTypes, sizeof(indicatorTypes) / sizeof(*indicatorTypes), _T("None"));
	initComboBox(m_Indicator4, indicatorTypes, sizeof(indicatorTypes) / sizeof(*indicatorTypes), _T("None"));

	m_ShowMonowaves.SetCheck(1);
	m_Volume.SetCheck(0);
	m_MajorVGrid.SetCheck(1);
	m_HGrid.SetCheck(1);

	m_MovAvg1.SetWindowText(_T("30"));
	m_MovAvg2.SetWindowText(_T("200"));

  ReloadRawData();
  // UpdateChart(&m_Chart);
  OnSelchangeChartsize();       // this will call fix the scrollbar and call UpdateChart
  int minScroll, maxScroll;
  m_WaveScroll.GetScrollRange(&minScroll, &maxScroll);
  m_WaveScroll.SetScrollPos(maxScroll, true);
}

/////////////////////////////////////////////////////////////////////////////
// CElliotEngineView printing

BOOL CElliotEngineView::OnPreparePrinting(CPrintInfo* pInfo)
{
  pInfo->SetMaxPage(1);
	// default preparation
	return DoPreparePrinting(pInfo);
}

void CElliotEngineView::OnBeginPrinting(CDC* pDC, CPrintInfo* pInfo)
{
	// TODO: add extra initialization before printing
  CFormView::OnBeginPrinting(pDC, pInfo);
}

void CElliotEngineView::OnEndPrinting(CDC* pDC, CPrintInfo* pInfo)
{
	// TODO: add cleanup after printing
  CFormView::OnEndPrinting(pDC, pInfo);
}

void CElliotEngineView::OnPrint(CDC* pDC, CPrintInfo* pInfo)
{
  RECT r;
  m_Chart.GetWindowRect(&r);
  CPoint pt(0,0);
  HBITMAP hBitmap = m_Chart.GetBitmap();
  CBitmap* pb = CBitmap::FromHandle(hBitmap);
  CSize size(r.right-r.left+1, r.bottom-r.top+1);

  int pageWidth = pDC->GetDeviceCaps(HORZRES);
  int pageHeight = pDC->GetDeviceCaps(VERTRES);
  double paperWidth = (double)pDC->GetDeviceCaps(HORZSIZE);
  double paperHeight = (double)pDC->GetDeviceCaps(VERTSIZE);

  pDC->SetMapMode(MM_ANISOTROPIC);
  pDC->SetWindowExt(size);

  pDC->SetViewportExt(pageWidth, pageWidth*size.cy/size.cx);//the "output pageHeight" is relativ to pageWidth
  pDC->SetViewportOrg(0, 0);

  pDC->DrawState(pt, size, hBitmap, DSS_NORMAL);
}

/////////////////////////////////////////////////////////////////////////////
// CElliotEngineView diagnostics

#ifdef _DEBUG
void CElliotEngineView::AssertValid() const
{
	CFormView::AssertValid();
}

void CElliotEngineView::Dump(CDumpContext& dc) const
{
	CFormView::Dump(dc);
}

CElliotEngineDoc* CElliotEngineView::GetDocument() // non-debug version is inline
{
	ASSERT(m_pDocument->IsKindOf(RUNTIME_CLASS(CElliotEngineDoc)));
	return (CElliotEngineDoc*)m_pDocument;
}
#endif //_DEBUG

/////////////////////////////////////////////////////////////////////////////
// CElliotEngineView message handlers

//
// ChartDirector outputs Device Independent Bitmaps in memory, while MFC
// expects HBITMAP. This utility converts from DIB in memory to HBITMAP.
//
static HBITMAP makeChartAsHBITMAP(HDC hdc, BaseChart *c)
{
	//output chart as Device Indpendent Bitmap with file headers
	MemBlock m = c->makeChart(BMP);

	//convert it to HBITMAP object
	return CreateDIBitmap(
		hdc, 
		(const struct tagBITMAPINFOHEADER *)(m.data + 14), 
		CBM_INIT, 
		m.data + *(int *)(m.data + 10), 
		(const struct tagBITMAPINFO *)(m.data + 14),
		DIB_RGB_COLORS);
}


void CElliotEngineView::OnSize(UINT nType, int cx, int cy) 
{
	CFormView::OnSize(nType, cx, cy);
	
	// TODO: Add your message handler code here
	
}


void CElliotEngineView::ReloadRawData()
{
  delete[] m_timeStamps;
  delete[] m_highData;
  delete[] m_lowData;
  delete[] m_openData;
  delete[] m_closeData;
  delete[] m_volData;
  m_noOfPoints = 0;
  m_timeStamps = NULL;
  m_highData = NULL;
  m_lowData = NULL;
  m_openData = NULL;
  m_closeData = NULL;
  m_volData = NULL;
  m_noOfRawPoints = 0;
  CElliotEngineDoc* pDoc = GetDocument();
  if (NULL == pDoc)
    return;

  PriceNodeVec* pPriceNodes = NULL;
  bool bAllocatedPriceNodes = false;

  // The duration selected by the user
  int durationInDays = (int)_tcstol((const TCHAR *)m_TimeRange.GetItemDataPtr(m_TimeRange.GetCurSel()), NULL, 0);

  if (durationInDays >= 4 * 360)
  {
    //4 years or more - use monthly points. Note that we need to add extra points
    //by shifting the starting month backwards
    m_resolution = MONTHSECONDS;
  }
  else 
  if (durationInDays >= 360)
  {
    //1 year or more - use weekly points.
    m_resolution = WEEKSECONDS;
  }
  else
  if (durationInDays >= 30)
  {
    //1 month or more - user daily points. Note that we need to add extra points
    //by shifting the starting day backwards. Also, we need to multiple by 7/5
    //because one week only have 5 trading days (5 points per 7 calender day).
    m_resolution = DAYSECONDS;
  }
  else 
  {
    // Less than 30 days duration. In this demo program, if it is less than 30 days,
    // the only choices are 10 days or less. So a 30-minute chart is a proper resolution.
    m_resolution = 1800;
  }

  if (m_resolution == pDoc->m_PriceNodeInterval || (pDoc->m_PriceNodesRaw.size() == 0 && m_resolution < pDoc->m_PriceNodeInterval))
  {
    pPriceNodes = &pDoc->m_PriceNodes;
    m_resolution = pDoc->m_PriceNodeInterval;
  }
  else
  {
    bAllocatedPriceNodes = true;
    pPriceNodes = new PriceNodeVec;
    PriceNodeVec* pSourceNodes = (pDoc->m_PriceNodesRaw.size() > 0 ? &pDoc->m_PriceNodesRaw : &pDoc->m_PriceNodes);
    EW_MergeDataIntoPeriods(*pSourceNodes, m_resolution, 1, *pPriceNodes);
  }

  int nodes = (pPriceNodes ? pPriceNodes->size() : 0);
  if (nodes >= 2)
  {
    m_timeStamps  = new double[nodes + durationInDays];
    m_highData    = new double[nodes + durationInDays];
    m_lowData     = new double[nodes + durationInDays];
    m_openData    = new double[nodes + durationInDays];
    m_closeData   = new double[nodes + durationInDays];
    m_volData     = new double[nodes + durationInDays];

    // now convert the points
    ETime d;
    PriceNodeVec::const_iterator it = pPriceNodes->begin();
    for (; it != pPriceNodes->end(); it++, m_noOfRawPoints++)
    {
      d = (*it).date;
      double f = 
      m_timeStamps[m_noOfRawPoints] = Chart::chartTime(d.GetYear(), d.GetMonth(), d.GetDay(), d.GetHour(), d.GetMinute(), d.GetSecond());
      m_highData[m_noOfRawPoints]   = (*it).high;
      m_lowData[m_noOfRawPoints]    = (*it).low;
      m_openData[m_noOfRawPoints]   = (*it).open;
      m_closeData[m_noOfRawPoints]  = (*it).close;
      m_volData[m_noOfRawPoints]    = (*it).volume;
    }
    for (; m_noOfRawPoints < nodes + 10; m_noOfRawPoints++)
    {
      d.MoveDays(m_resolution / DAYSECONDS, WEEKDAY_ONLY);
      m_timeStamps[m_noOfRawPoints] = Chart::chartTime(d.GetYear(), d.GetMonth(), d.GetDay(), d.GetHour(), d.GetMinute(), d.GetSecond());
      m_highData[m_noOfRawPoints] = m_lowData[m_noOfRawPoints] = m_openData[m_noOfRawPoints] = m_closeData[m_noOfRawPoints] = m_volData[m_noOfRawPoints] = NoValue;
    }
  }
  if (bAllocatedPriceNodes)
    delete pPriceNodes;
  int maxScroll = max(m_noOfRawPoints - 25, 0);
  m_ChartScrollBar.SetScrollRange(0, maxScroll, true);
  m_ChartScrollBar.SetScrollPos(maxScroll, true);

  // if we're showing weeks or months, when the monowaves have a daily resolution, it won't work...
	m_ShowMonowaves.SetCheck(m_resolution <= pDoc->m_PriceNodeInterval);
}

/// <summary>
/// Get the requested data from the data source, and store the data in the member
/// array variables timeStamps, volData, highData, lowData, openData, closeData. 
/// Also set the member variables startDate, endDate and resolution to reflect the
/// actual data points retrieved.
/// </summary>
/// <param name="requestedDuration">The duration in days as requested by the user.</param>
/// <param name="requestedExtraPoints">The number of extra leading points requested.</param>
void CElliotEngineView::GetData(int requestedDuration, int requestedExtraPoints)
{
  m_noOfPoints = 0;

  int minScroll, maxScroll, scrollPos;
  m_ChartScrollBar.GetScrollRange(&minScroll, &maxScroll);
  scrollPos = m_ChartScrollBar.GetScrollPos();
  //
  // The first step is to obtain the startDate and endDate of the requested data.
  //
  // Note that the startDate above is the axis start date. To also get the 
  // requestedExtraPoints (the leading points before the startDate for moving
  // averages computation), the data retrieval start date will be adjusted to:
  //
  //	 dataQueryStartDate = startDate - requestedExtraPoints * resolution
  //
  // The above code is a simplification because in practice, we need to use
  // trading days (instead of calendar dates) for the date/time computation.
  // For example, if the duration is 3 days, the user expects it to mean 3
  // trading days (with holidays skipped).
  //
  if (m_noOfRawPoints <= 1)
    return;
  int node = m_noOfRawPoints-1 - (maxScroll-scrollPos);
  if (node < 1)
    node = 1;
  int YMD;
  m_endDate = m_timeStamps[node];

  //
  // After we obtain the endDate, we get the startDate based on the user selected
  // duration. It is OK to obtain more data than requested.
  //
  if (requestedDuration > 400)
  {
    // More than a year - so we use months as the unit
    YMD = Chart::getChartYMD(m_endDate);
    int startMonth = (YMD / 100) % 100 - requestedDuration / 30;
    int startYear = YMD / 10000;
    while (startMonth < 1)
    {
      --startYear;
      startMonth += 12;
    }
    m_startDate = Chart::chartTime(startYear, startMonth, 1);
  }
  else
  {
    // Less than 30 days - use day as the unit. Note that we use trading days
    // below. For less than 30 days, the starting point of the axis is always at
    // the start of the day (9:30am)
    m_startDate = m_endDate - fmod(m_endDate, 86400) + ETime::m_TradingDayOpen;
    for (int i = 1; i < requestedDuration; ++i)
    {
      if (Chart::getChartWeekDay(m_startDate) == 1)
        m_startDate -= 3 * 86400;
      else
        m_startDate -= 86400;
    }
  }

  // now calculate the startdate where we start collecting the "extra" points
  node = 0;
  double currentDate;
  if (m_resolution == MONTHSECONDS)
  {
    YMD = Chart::getChartYMD(m_startDate);
    int currentMonth = (YMD / 100) % 100 - requestedExtraPoints;
    int currentYear = YMD / 10000;
    while (currentMonth < 1)
    {
        --currentYear;
        currentMonth += 12;
    }

    currentDate = Chart::chartTime(currentYear, currentMonth, 1);
  }
  else 
  if (m_resolution == WEEKSECONDS)
  {
    //always start on Monday
    while (Chart::getChartWeekDay(m_startDate) != 1)
        m_startDate -= 86400;

    //Note that we need to add extra points by shifting the starting weeks backwards
    currentDate = m_startDate - requestedExtraPoints * 7 * 86400;
  }
  else
  if (m_resolution == DAYSECONDS)
  {
    //1 month or more - user daily points. Note that we need to add extra points
    //by shifting the starting day backwards. Also, we need to multiple by 7/5
    //because one week only have 5 trading days (5 points per 7 calender day).
    currentDate = m_startDate - fmod(m_startDate, 86400) - (requestedExtraPoints * 7 + 4) / 5 * 86400;

    //Remember to skip non-trading days
    if (Chart::getChartWeekDay(currentDate) == 0)
        currentDate -= 2 * 86400;
    else if (Chart::getChartWeekDay(currentDate) == 6)
        currentDate -= 86400;
  }
  else 
  {
    //We need to adjust the startDate for the requestedExtraPoints by shifting the time
    //backwards. We need to determine how many days to shift backwards. We assume each
    //day has 6.5 hours of trading time (9:30am - 16:00pm)
    double dataPointsPerDay = (ETime::m_TradingDayClose - ETime::m_TradingDayOpen) / m_resolution;
    currentDate = m_startDate - fmod(m_startDate, 86400) - 
                  (int)(requestedExtraPoints / dataPointsPerDay * 7 / 5 + 0.9999999) * 86400;

    //Remember to skip non-trading days
    if (Chart::getChartWeekDay(currentDate) == 0)
      currentDate -= 2 * 86400;
    else
    if (Chart::getChartWeekDay(currentDate) == 6)
      currentDate -= 86400;
  }

  // find this date in the actual data set
  while (m_timeStamps[node] < currentDate)
    node++;
  m_offsetIntoRawArrays = node;
  //Now count the number of points to use
  while (node < m_noOfRawPoints && m_timeStamps[node] <= m_endDate)
  {
    node++;
  }
  m_noOfPoints = node - m_offsetIntoRawArrays;
}


int CElliotEngineView::DrawWave(const ETime& startDate, double startPrice, const ETime& endDate, double endPrice, double* pts)
{
  // find out where in the timestamp/price arrays the startDate is
  int i = 0;
  ETime date = ChartDirectorDate2ETime(m_timeStamps[i+m_offsetIntoRawArrays]);
  while (date < startDate && i<m_noOfPoints)
  {
    ++i;
    date = ChartDirectorDate2ETime(m_timeStamps[i+m_offsetIntoRawArrays]);
  }
  
  double node_value = startPrice;
  if (date <= startDate && i<m_noOfPoints)
  {
    pts[i++] = node_value;
    date = ChartDirectorDate2ETime(m_timeStamps[i+m_offsetIntoRawArrays]);
  }

  // Find out where the endDate is
  int node = i;
  while (date < endDate && i<m_noOfPoints)
  {
    i++;
    date = ChartDirectorDate2ETime(m_timeStamps[i+m_offsetIntoRawArrays]);
  }

  // paint a line (downward or upward) as M1 progresses
  float f = (endPrice - startPrice) / (i - node + 1);
  node_value = startPrice + f;
  while (node <= i)
  {
    pts[node++] = node_value;
    node_value += f;
  }
  return node;
}


int CElliotEngineView::AddMonoWaves(XYChart* pMainChart)
{
  //Add an orange (0xff9933) scatter chart layer, using 13 pixel diamonds as
  //symbols

  int num_monowaves = 0;
  CElliotEngineDoc* pDoc = GetDocument();
  int node = 0;
  int nodes = pDoc->m_MonoWaves.size();

  if (nodes < 1)
    return num_monowaves;

  std::map<int, int> node2chartMap;
  double* pts = new double[m_noOfPoints+10];
  ETime node_date = ChartDirectorDate2ETime(m_startDate);
  while (node < nodes && pDoc->m_MonoWaves[node].StartDate() < node_date)
    node++;
  if (node >= nodes)
    return num_monowaves;

  node_date = pDoc->m_MonoWaves[node].StartDate();
  float node_value = pDoc->m_MonoWaves[node].StartPrice();

  int i = 0;
  while (m_timeStamps[i+m_offsetIntoRawArrays] < m_startDate && i<m_noOfPoints)
    pts[i++] = NoValue;
  const int first_point_on_chart = m_leadingExtraPoints;

  ETime date;
  for (; i<m_noOfPoints; i++)
  {
    date = ChartDirectorDate2ETime(m_timeStamps[i+m_offsetIntoRawArrays]);
    while (date < node_date && i<m_noOfPoints)
    {
      pts[i++] = NoValue;
      date = ChartDirectorDate2ETime(m_timeStamps[i+m_offsetIntoRawArrays]);
    }

    if (i<m_noOfPoints)
    {
      pts[i] = node_value;
      node2chartMap[node] = i;
    }

    while (node < nodes && node_date <= date)
    {
      num_monowaves++;
      node_date = pDoc->m_MonoWaves[node].EndDate();
      node_value = pDoc->m_MonoWaves[node].EndPrice();
      node++;
    }
    if (node >= nodes)
      node_date.Change(2200, 1, 1);
  }
  DoubleArray data(pts, m_noOfPoints);

  DoubleArray dummy;
  ScatterLayer* pScatter = pMainChart->addScatterLayer(dummy, data, "Monowaves", Chart::DiamondSymbol, 13, 0xff9933);

  // add text labels!
  pScatter->setDataLabelStyle();
  char buf[10];
  std::map<int, int>::const_iterator it = node2chartMap.begin();
  for (;it != node2chartMap.end(); it++)
  {
    node = (*it).first - 1;
    if (node >= 0)
    {
      i = (*it).second - first_point_on_chart;
      if (0 == pDoc->m_MonoWaves[node].mCategory)
        sprintf(buf, "%d%c", pDoc->m_MonoWaves[node].mRetracementRule, pDoc->m_MonoWaves[node].mCondition);
      else
        sprintf(buf, "%d%c%d", pDoc->m_MonoWaves[node].mRetracementRule, pDoc->m_MonoWaves[node].mCondition, pDoc->m_MonoWaves[node].mCategory);
      double angle = (pDoc->m_MonoWaves[node].LengthInPrice() >= 0.0f ? 45.0 : -45.0);
      pScatter->addCustomDataLabel(0, i, buf, NULL, 8, Chart::TextColor, angle);
    }
  }

  //
  // now add representation of the "current monowave under observation"
  //
  double* pts2 = new double[m_noOfPoints+10];
  double* pts3 = new double[m_noOfPoints+10];
  int minScroll, maxScroll;
  m_WaveScroll.GetScrollRange(&minScroll, &maxScroll);
  int pos = m_WaveScroll.GetScrollPos();
  int m1 = node - (maxScroll - pos);
  for (i=0; i<m_noOfPoints; i++)
    pts3[i] = pts2[i] = NoValue;

  if (m1 >= 0 && m1 < nodes)
  {
    const WaveNode& M1 = pDoc->m_MonoWaves[m1];
    WaveNode M_minus_1, M0, M2, M3;

#ifdef INCLUDE_SPECULATIVE_STATISTICS
    //
    // start speculative statistical comparison
    // not yet ready for prime-time...
    // 
    std::map<int, int> matches;
    i = EW_FindSimilarWaveSequences(pDoc->m_MonoWaves, m1, matches);
    std::map<int, int>::const_iterator it = matches.begin();
    for (; it != matches.end(); it++)
    {
      double* ptsX = new double[m_noOfPoints+10];
      for (i=0; i<m_noOfPoints; i++)
        ptsX[i] = NoValue;
      node = (*it).first;
      float scale = M1.LengthInPrice() / pDoc->m_MonoWaves[node].LengthInPrice();
      float displacement = pDoc->m_MonoWaves[node].EndPrice();

      for (i = -(*it).second; i < 6 && (node+i>=0) && (node+i<nodes) && (m1+i>=0) && (m1+i<nodes); i++)
      {
        const WaveNode& Mi = pDoc->m_MonoWaves[node+i];
        const WaveNode& M1i = pDoc->m_MonoWaves[m1+i];
        DrawWave(M1i.StartDate(), (Mi.StartPrice() - displacement) * scale + M1.EndPrice(), M1i.EndDate(), (Mi.EndPrice() - displacement) * scale + M1.EndPrice(), ptsX);
      }

      DoubleArray dataX(ptsX, m_noOfPoints);
      LineLayer* pLineLayer = pMainChart->addLineLayer(dataX, 0x208020, "precedents");
      pLineLayer->setLineWidth(3);
    }
    //
    // end speculative statistical comparison
    // 
#endif // INCLUDE_SPECULATIVE_STATISTICS

    // Draw M1
    DrawWave(M1.StartDate(), M1.StartPrice(), M1.EndDate(), M1.EndPrice(), pts2);

    if (EW_FindM0(pDoc->m_MonoWaves, M1, m1, M0))
    {
      // Draw M0
      DrawWave(M0.StartDate(), M0.StartPrice(), M0.EndDate(), M0.EndPrice(), pts3);

      if (EW_FindM0(pDoc->m_MonoWaves, M0, m1, M_minus_1))
      {
        // Draw M-1
        DrawWave(M_minus_1.StartDate(), M_minus_1.StartPrice(), M_minus_1.EndDate(), M_minus_1.EndPrice(), pts3);
      }
    }
    
    if (EW_FindM2(pDoc->m_MonoWaves, M1, m1, M2))
    {
      // Draw M2
      DrawWave(M2.StartDate(), M2.StartPrice(), M2.EndDate(), M2.EndPrice(), pts3);

      if (EW_FindM2(pDoc->m_MonoWaves, M2, m1, M3))
      {
        // Draw M3
        DrawWave(M3.StartDate(), M3.StartPrice(), M3.EndDate(), M3.EndPrice(), pts3);
      }
    }

    DoubleArray data2(pts2, m_noOfPoints);
    LineLayer* pLineLayer = pMainChart->addLineLayer(data2, 0x0000ff, "m1");
    pLineLayer->setLineWidth(9);

    DoubleArray data3(pts3, m_noOfPoints);
    LineLayer* pLineLayer3 = pMainChart->addLineLayer(data3, 0xff0000, "m-1,m0,m2,m3");
    pLineLayer3->setLineWidth(7);
  }
  delete[] pts;
  delete[] pts2;
  delete[] pts3;

  return num_monowaves;
}


/// <summary>
/// Add a moving average line to the FinanceChart object.
/// </summary>
/// <param name="m">The FinanceChart object to add the line to.</param>
/// <param name="avgType">The moving average type (SMA/EMA/TMA/WMA).</param>
/// <param name="avgPeriod">The moving average period.</param>
/// <param name="color">The color of the line.</param>
static void addMovingAvg(FinanceChart *m, CString avgType, int avgPeriod, int color)
{
  if (avgPeriod > 1)
  {
    if (avgType == _T("SMA"))
      m->addSimpleMovingAvg(avgPeriod, color);
    else if (avgType == _T("EMA"))
      m->addExpMovingAvg(avgPeriod, color);
    else if (avgType == _T("TMA"))
      m->addTriMovingAvg(avgPeriod, color);
    else if (avgType == _T("WMA"))
      m->addWeightedMovingAvg(avgPeriod, color);
  }
}


/// <summary>
/// Add an indicator chart to the FinanceChart object. In this demo example, the indicator
/// parameters (such as the period used to compute RSI, colors of the lines, etc.) are hard
/// coded to commonly used values. You are welcome to design a more complex user interface 
/// to allow users to set the parameters.
/// </summary>
/// <param name="m">The FinanceChart object to add the line to.</param>
/// <param name="indicator">The selected indicator.</param>
/// <param name="height">Height of the chart in pixels</param>
static void addIndicator(FinanceChart *m, CString indicator, int height)
{
  if (indicator == _T("RSI"))
      m->addRSI(height, 14, 0x800080, 20, 0xff6666, 0x6666ff);
  else if (indicator == _T("StochRSI"))
      m->addStochRSI(height, 14, 0x800080, 30, 0xff6666, 0x6666ff);
  else if (indicator == _T("MACD"))
      m->addMACD(height, 26, 12, 9, 0xff, 0xff00ff, 0x8000);
  else if (indicator == _T("FStoch"))
      m->addFastStochastic(height, 14, 3, 0x6060, 0x606000);
  else if (indicator == _T("SStoch"))
      m->addSlowStochastic(height, 14, 3, 0x6060, 0x606000);
  else if (indicator == _T("ATR"))
      m->addATR(height, 14, 0x808080, 0xff);
  else if (indicator == _T("ADX"))
      m->addADX(height, 14, 0x8000, 0x800000, 0x80);
  else if (indicator == _T("DCW"))
      m->addDonchianWidth(height, 20, 0xff);
  else if (indicator == _T("BBW"))
      m->addBollingerWidth(height, 20, 2, 0xff);
  else if (indicator == _T("DPO"))
      m->addDPO(height, 20, 0xff);
  else if (indicator == _T("PVT"))
      m->addPVT(height, 0xff);
  else if (indicator == _T("Momentum"))
      m->addMomentum(height, 12, 0xff);
  else if (indicator == _T("Performance"))
      m->addPerformance(height, 0xff);
  else if (indicator == _T("ROC"))
      m->addROC(height, 12, 0xff);
  else if (indicator == _T("OBV"))
      m->addOBV(height, 0xff);
  else if (indicator == _T("AccDist"))
      m->addAccDist(height, 0xff);
  else if (indicator == _T("CLV"))
      m->addCLV(height, 0xff);
  else if (indicator == _T("WilliamR"))
      m->addWilliamR(height, 14, 0x800080, 30, 0xff6666, 0x6666ff);
  else if (indicator == _T("Aroon"))
      m->addAroon(height, 14, 0x339933, 0x333399);
  else if (indicator == _T("AroonOsc"))
      m->addAroonOsc(height, 14, 0xff);
  else if (indicator == _T("CCI"))
      m->addCCI(height, 20, 0x800080, 100, 0xff6666, 0x6666ff);
  else if (indicator == _T("EMV"))
      m->addEaseOfMovement(height, 9, 0x6060, 0x606000);
  else if (indicator == _T("MDX"))
      m->addMassIndex(height, 0x800080, 0xff6666, 0x6666ff);
  else if (indicator == _T("CVolatility"))
      m->addChaikinVolatility(height, 10, 10, 0xff);
  else if (indicator == _T("COscillator"))
      m->addChaikinOscillator(height, 0xff);
  else if (indicator == _T("CMF"))
      m->addChaikinMoneyFlow(height, 21, 0x8000);
  else if (indicator == _T("NVI"))
      m->addNVI(height, 255, 0xff, 0x883333);
  else if (indicator == _T("PVI"))
      m->addPVI(height, 255, 0xff, 0x883333);
  else if (indicator == _T("MFI"))
      m->addMFI(height, 14, 0x800080, 30, 0xff6666, 0x6666ff);
  else if (indicator == _T("PVO"))
      m->addPVO(height, 26, 12, 9, 0xff, 0xff00ff, 0x8000);
  else if (indicator == _T("PPO"))
      m->addPPO(height, 26, 12, 9, 0xff, 0xff00ff, 0x8000);
  else if (indicator == _T("UO"))
      m->addUltimateOscillator(height, 7, 14, 28, 0x800080, 20, 0xff6666, 0x6666ff);
  else if (indicator == _T("Vol"))
      m->addVolIndicator(height, 0x99ff99, 0xff9999, 0xc0c0c0);
  else if (indicator == _T("TRIX"))
      m->addTRIX(height, 12, 0xff);
}


/// <summary>
/// Draw the chart according to user selection and display it in the WebChartViewer.
/// </summary>
/// <param name="viewer">The WebChartViewer object to display the chart.</param>
void CElliotEngineView::UpdateChart(CChartViewer *viewer)
{
  //
  // To draw a chart, we need data first. To retrieve data, we need the chart 
  // duration and the moving average period. The latter is needed because we need 
  // extra leading data points to compute moving averages.
  //
  CElliotEngineDoc* pDoc = GetDocument();
  if (NULL == pDoc)
    return;

  // The duration selected by the user
  int durationInDays = (int)_tcstol((const TCHAR *)m_TimeRange.GetItemDataPtr(
  m_TimeRange.GetCurSel()), NULL, 0);

  // The first moving average period selected by the user.
  CString avgText;
  m_MovAvg1.GetWindowText(avgText);
  m_avgPeriod1 = (int)_tcstol(avgText, NULL, 0);
  if (m_avgPeriod1 < 0)
      m_avgPeriod1 = 0;
  if (m_avgPeriod1 > 300)
      m_avgPeriod1 = 300;

  // The second moving average period selected by the user.
  m_MovAvg2.GetWindowText(avgText);
  m_avgPeriod2 = (int)_tcstol(avgText, NULL, 0);
  if (m_avgPeriod2 < 0)
      m_avgPeriod2 = 0;
  if (m_avgPeriod2 > 300)
      m_avgPeriod2 = 300;

  // We need extra leading data points in order to compute moving averages and also
  // various indicators. For simplicity, we just hard coded to at least 25 leading
  // points irrespective of what indicators the user has chosen to display.
  m_leadingExtraPoints = (m_avgPeriod1 > m_avgPeriod2) ? m_avgPeriod1 : m_avgPeriod2;
  if (m_leadingExtraPoints < 25)
    m_leadingExtraPoints = 25;

  // Get the data from the data source. This method should get the data into the 
  // member variables timeStamps, volData, highData, lowData, openData, closeData as 
  // well as providing the data range description startDate, endDate and resolution.
  GetData(durationInDays, m_leadingExtraPoints);

  // 
  // Data points that are before the startDate are the leading data points for
  // computing moving averages. This may be different from the extraPoints we 
  // requested (eg. the database may have no such data), so we need to detect
  // the actual number of leading points.
  //
  for (m_leadingExtraPoints = m_offsetIntoRawArrays; m_leadingExtraPoints < m_noOfPoints+m_offsetIntoRawArrays; ++m_leadingExtraPoints)
  {
    if (m_timeStamps[m_leadingExtraPoints] >= m_startDate)
      break;
  }
  m_leadingExtraPoints -= m_offsetIntoRawArrays;

  // Check if there is any valid data
  if (m_leadingExtraPoints >= m_noOfPoints+m_offsetIntoRawArrays)
  {
    // No data - just display the no data message.
    MultiChart errMsg(400, 50);
    errMsg.addTitle(Chart::TopLeft, "No data available for the specified time period", 
    "arial.ttf", 10);
    viewer->setChart(&errMsg);
    return;
  }

  // In some finance chart presentation style, even if the data for the latest day 
  // is not fully available, the axis for the entire day will still be drawn, where
  // no data will appear near the end of the axis.
  double *extendedTimeStamps = m_timeStamps + m_offsetIntoRawArrays;
  int extraTrailingPoints = 0;
  if (m_resolution <= 86400)
  {
    // Add extra points to the axis until it reaches the end of the day. The end
    // of day is assumed to be 16:00 (it depends on the stock exchange).
    double lastTime = m_timeStamps[m_noOfPoints + m_offsetIntoRawArrays - 1];
    extraTrailingPoints = (int)((ETime::m_TradingDayClose - fmod(lastTime, 86400)) / m_resolution);
    if (extraTrailingPoints <= 0)
      extraTrailingPoints = 0;
    else
    {
      extendedTimeStamps = new double[m_noOfPoints + extraTrailingPoints];
      memcpy(extendedTimeStamps, m_timeStamps + m_offsetIntoRawArrays, sizeof(double) * m_noOfPoints);
      for (int i = 0; i < extraTrailingPoints; ++i)
        extendedTimeStamps[m_noOfPoints + i] = lastTime + m_resolution * (i + 1);
    }
  }

  //
  // At this stage, all data is available. We can draw the chart as according to 
  // user input.
  //

  //
  // Determine the chart size. In this demo, user can select 4 different chart sizes.
  // Default is the large chart size.
  //
  int width = 1000;			// width of chart
  int mainHeight = 320;		// height of main chart
  int indicatorHeight = 90;	// height of indicator chart

  CString selectedSize = (const TCHAR *)m_ChartSize.GetItemDataPtr(m_ChartSize.GetCurSel());
  if (selectedSize == _T("S"))
  {
    // Small chart size
    width = 620;
    mainHeight = 210;
    indicatorHeight = 65;
  }
  else if (selectedSize == _T("M"))
  {
    // Medium chart size
    width = 780;
    mainHeight = 250;
    indicatorHeight = 80;
  }
  else if (selectedSize == _T("H"))
  {
    // Huge chart size
    width = 1200;
    mainHeight = 500;
    indicatorHeight = 100;
  }

  // Create the chart object using the selected size
  FinanceChart m(width);

  // Set the data into the chart object
  m.setData(DoubleArray(extendedTimeStamps, m_noOfPoints + extraTrailingPoints), 
            DoubleArray(m_highData  + m_offsetIntoRawArrays, m_noOfPoints), 
            DoubleArray(m_lowData   + m_offsetIntoRawArrays, m_noOfPoints), 
            DoubleArray(m_openData  + m_offsetIntoRawArrays, m_noOfPoints), 
            DoubleArray(m_closeData + m_offsetIntoRawArrays, m_noOfPoints),
            DoubleArray(m_volData   + m_offsetIntoRawArrays, m_noOfPoints), m_leadingExtraPoints);

  // The extendedTimeStamps are not needed any more - can free it
  // TODO: fix
  if (extraTrailingPoints)
    delete[] extendedTimeStamps;

  //
  // We configure the title of the chart. In this demo chart design, we put the 
  // company name as the top line of the title with left alignment.
  //
  CString title = pDoc->GetTitle();
  m.addPlotAreaTitle(Chart::TopLeft, title);

  // We displays the current date as well as the data resolution on the next line.
  const char *resolutionText = "";
  if (m_resolution == 30 * 86400)
      resolutionText = "Monthly";
  else if (m_resolution == 7 * 86400)
      resolutionText = "Weekly";
  else if (m_resolution == 86400)
      resolutionText = "Daily";
  else if (m_resolution == 900)
      resolutionText = "15-min";

  char buffer[1024];
  sprintf(buffer, "<*font=arial.ttf,size=8*>%s - %s chart", 
  m.formatValue(Chart::chartTime2(time(NULL)), "mmm dd, yyyy"), resolutionText);
  m.addPlotAreaTitle(Chart::BottomLeft, buffer);

  // A copyright message at the bottom left corner the title area
  m.addPlotAreaTitle(Chart::BottomRight, 
  "<*font=arial.ttf,size=8*>(c) Advanced Software Engineering");

  //
  // Set the grid style according to user preference. In this simple demo user
  // interface, the user can enable/disable grid lines. The grid line colors are
  // hard coded to 0xdddddd (light grey), and the plot area background color is 
  // hard coded to 0xfffff0 (pale yellow).
  //
  int majorVGridColor = m_MajorVGrid.GetCheck() ? 0xdddddd : Chart::Transparent;
  int minorVGridColor = m_MinorVGrid.GetCheck() ? 0xdddddd : Chart::Transparent;
  int hGridColor = m_HGrid.GetCheck() ? 0xdddddd : Chart::Transparent;
  m.setPlotAreaStyle(0xfffff0, hGridColor, majorVGridColor, hGridColor, minorVGridColor);

  //
  // Set log or linear scale according to user preference
  //
  m.setLogScale(m_LogScale.GetCheck() != 0);

  //
  // Add the first techical indicator according. In this demo, we draw the first
  // indicator on top of the main chart.
  //
  addIndicator(&m, (const TCHAR *)m_Indicator1.GetItemDataPtr(m_Indicator1.GetCurSel()), 
  indicatorHeight);

  // Add the main chart
  XYChart* pMainChart = m.addMainChart(mainHeight);

  //
  // Draw the main chart depending on the chart type the user has selected
  //
  CString selectedType = (const TCHAR *)m_ChartType.GetItemDataPtr(m_ChartType.GetCurSel());
  if (selectedType == _T("Close"))
      m.addCloseLine(0x40);
  else if (selectedType == _T("TP"))
      m.addTypicalPrice(0x40);
  else if (selectedType == _T("WC"))
      m.addWeightedClose(0x40);
  else if (selectedType == _T("Median"))
      m.addMedianPrice(0x40);

  //
  // Add moving average lines.
  //
  addMovingAvg(&m, (const TCHAR *)m_AvgType1.GetItemDataPtr(m_AvgType1.GetCurSel()), 
  m_avgPeriod1, 0x663300);
  addMovingAvg(&m, (const TCHAR *)m_AvgType2.GetItemDataPtr(m_AvgType2.GetCurSel()), 
  m_avgPeriod2, 0x9900ff);

  //
  // Draw the main chart if the user has selected CandleStick or OHLC. We
  // draw it here to make sure it is drawn behind the moving average lines
  // (that is, the moving average lines stay on top.)
  //
  if (selectedType == _T("CandleStick"))
      m.addCandleStick(0x33ff33, 0xff3333);
  else if (selectedType == _T("OHLC"))
      m.addHLOC(0x8000, 0x800000);

  //
  // Add price band/channel/envelop to the chart according to user selection
  //
  CString selectedBand = (const TCHAR *)m_Band.GetItemDataPtr(m_Band.GetCurSel());
  if (selectedBand == _T("BB"))
      m.addBollingerBand(20, 2, 0x9999ff, 0xc06666ff);
  else if (selectedBand == _T("DC"))
      m.addDonchianChannel(20, 0x9999ff, 0xc06666ff);
  else if (selectedBand == _T("Envelop"))
      m.addEnvelop(20, 0.1, 0x9999ff, 0xc06666ff);

  //
  // Add volume bars to the main chart if necessary
  //
  if (m_Volume.GetCheck())
      m.addVolBars(indicatorHeight, 0x99ff99, 0xff9999, 0xc0c0c0);

  //
  // Add additional indicators as according to user selection.
  //
  addIndicator(&m, (const TCHAR *)m_Indicator2.GetItemDataPtr(m_Indicator2.GetCurSel()), 
  indicatorHeight);
  addIndicator(&m, (const TCHAR *)m_Indicator3.GetItemDataPtr(m_Indicator3.GetCurSel()), 
  indicatorHeight);
  addIndicator(&m, (const TCHAR *)m_Indicator4.GetItemDataPtr(m_Indicator4.GetCurSel()), 
  indicatorHeight);

  if (m_ShowMonowaves.GetCheck())
  {
    int waves = AddMonoWaves(pMainChart);
    m_WaveScroll.SetScrollRange(0, waves, true);
    m_WaveScroll.EnableWindow(TRUE);
  }
  else
    m_WaveScroll.EnableWindow(FALSE);

  viewer->setChart(&m);
  sprintf(buffer, "title='%s {value|G}'", m.getToolTipDateFormat());
  viewer->setImageMap(m.getHTMLImageMap("", "", buffer));
}


//
// User selection has changed - update the chart
//
void CElliotEngineView::OnSelectChange() 
{
	UpdateChart(&m_Chart);
}


//
// User has entered text for the moving average window size
// - update chart if they are changed
//
void CElliotEngineView::OnTextChange() 
{
	CString avgText;
	m_MovAvg1.GetWindowText(avgText);
	int new_avgPeriod1 = (int)_tcstol(avgText, NULL, 0);
	
	m_MovAvg2.GetWindowText(avgText);
	int new_avgPeriod2 = (int)_tcstol(avgText, NULL, 0);

	if ((new_avgPeriod1 != m_avgPeriod1) || (new_avgPeriod2 != m_avgPeriod2))
		OnSelectChange();
}

void CElliotEngineView::OnSelchangeChartsize() 
{
  OnSelectChange();

  CRect scrollRect, viewerRect;
  m_ChartScrollBar.GetWindowRect(&scrollRect);
  m_Chart.GetWindowRect(&viewerRect);
	ScreenToClient(scrollRect);
	ScreenToClient(viewerRect);
  int scrollHeight = scrollRect.bottom - scrollRect.top;
  scrollRect.left  = viewerRect.left;
  scrollRect.right = viewerRect.right;
  scrollRect.top   = viewerRect.bottom;
  scrollRect.bottom = scrollRect.top + scrollHeight;
  m_ChartScrollBar.MoveWindow(&scrollRect, true);

  scrollRect.top += 20;
  scrollRect.bottom += 20;
  m_WaveScroll.MoveWindow(&scrollRect, true);
}

void CElliotEngineView::OnHScroll(UINT nSBCode, UINT nPos, CScrollBar* pScrollBar) 
{
	// TODO: Add your message handler code here and/or call default
  CElliotEngineDoc* pDoc = GetDocument();
  if (NULL != pDoc && pScrollBar == &m_ChartScrollBar)
  {
    int minScroll, maxScroll, pos;
    pScrollBar->GetScrollRange(&minScroll, &maxScroll);
    pos = pScrollBar->GetScrollPos();
    switch (nSBCode)
    {
      case SB_LEFT:             // Scroll to far left.
        pos = 0;
        break;
      case SB_ENDSCROLL:        // End scroll.
        // pos = maxScroll;
        break;
      case SB_LINELEFT:         // Scroll left.
        if (pos > 0)
          pos--;
        break;
      case SB_LINERIGHT:        // Scroll right.
        if (pos < maxScroll)
          pos++;
        break;
      case SB_PAGELEFT:         // Scroll one page left.
        pos -= m_noOfPoints / 2;
        if (pos < 0)
          pos = 0;
        break;
      case SB_PAGERIGHT:        // Scroll one page right.
        pos += m_noOfPoints / 2;
        if (pos > maxScroll)
          pos = maxScroll;
        break;
      case SB_RIGHT:            // Scroll to far right.
        pos = maxScroll;
        break;
      case SB_THUMBPOSITION:    // Scroll to absolute position. The current position is specified by the nPos parameter.
      case SB_THUMBTRACK:       //Drag scroll box to specified position. The current position is specified by the nPos parameter.
        pos = nPos;
        break;
    }
    pScrollBar->SetScrollPos(pos, nSBCode == SB_ENDSCROLL);
    if (nSBCode == SB_ENDSCROLL)
      UpdateChart(&m_Chart);
  }
  else
  if (NULL != pDoc && pScrollBar == &m_WaveScroll)
  {
    int minScroll, maxScroll, pos;
    pScrollBar->GetScrollRange(&minScroll, &maxScroll);
    pos = pScrollBar->GetScrollPos();
    switch (nSBCode)
    {
      case SB_LEFT:             // Scroll to far left.
        pos = 0;
        break;
      case SB_ENDSCROLL:        // End scroll.
        // pos = maxScroll;
        break;
      case SB_LINELEFT:         // Scroll left.
        if (pos > 0)
          pos--;
        break;
      case SB_LINERIGHT:        // Scroll right.
        if (pos < maxScroll)
          pos++;
        break;
      case SB_PAGELEFT:         // Scroll one page left.
        pos -= 10;
        if (pos < 0)
          pos = 0;
        break;
      case SB_PAGERIGHT:        // Scroll one page right.
        pos += 10;
        if (pos > maxScroll)
          pos = maxScroll;
        break;
      case SB_RIGHT:            // Scroll to far right.
        pos = maxScroll;
        break;
      case SB_THUMBPOSITION:    // Scroll to absolute position. The current position is specified by the nPos parameter.
      case SB_THUMBTRACK:       //Drag scroll box to specified position. The current position is specified by the nPos parameter.
        pos = nPos;
        break;
    }
    pScrollBar->SetScrollPos(pos, nSBCode == SB_ENDSCROLL);
    if (nSBCode == SB_ENDSCROLL)
      UpdateChart(&m_Chart);
  }	
  CFormView::OnHScroll(nSBCode, nPos, pScrollBar);
}

void CElliotEngineView::OnMouseMove(UINT nFlags, CPoint point) 
{
	// TODO: Add your message handler code here and/or call default
	
	CFormView::OnMouseMove(nFlags, point);
}

void CElliotEngineView::OnResolutionChange() 
{
  ReloadRawData();
  OnSelectChange();
}
