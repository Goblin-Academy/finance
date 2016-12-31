// ElliotEngineView.h : interface of the CElliotEngineView class
//
/////////////////////////////////////////////////////////////////////////////

#if !defined(AFX_ELLIOTENGINEVIEW_H__6022A139_5151_45DC_95EB_202FEBC1912E__INCLUDED_)
#define AFX_ELLIOTENGINEVIEW_H__6022A139_5151_45DC_95EB_202FEBC1912E__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
#include "FinanceChart.h"
#include "./ChartDirector/mfcdemo/mfcdemo/ChartViewer.h"

class CElliotEngineView : public CFormView
{
protected: // create from serialization only
	CElliotEngineView();
	DECLARE_DYNCREATE(CElliotEngineView)

public:
	//{{AFX_DATA(CElliotEngineView)
	enum { IDD = IDC_STATIC2 };
	CButton	m_ShowMonowaves;
	CScrollBar	m_ChartScrollBar;
	CScrollBar	m_WaveScroll;
	CEdit	m_MovAvg2;
	CEdit	m_MovAvg1;
	CButton	m_MinorVGrid;
	CButton	m_MajorVGrid;
	CButton	m_LogScale;
	CButton	m_HGrid;
	CButton	m_Volume;
	CComboBox	m_Indicator4;
	CComboBox	m_Indicator3;
	CComboBox	m_Indicator2;
	CComboBox	m_Indicator1;
	CComboBox	m_ChartType;
	CComboBox	m_ChartSize;
	CComboBox	m_Band;
	CComboBox	m_AvgType2;
	CComboBox	m_AvgType1;
	CComboBox	m_TimeRange;
	CChartViewer	m_Chart;
	//}}AFX_DATA

// Attributes
public:
	CElliotEngineDoc* GetDocument();

// Operations
public:

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CElliotEngineView)
	public:
	virtual BOOL PreCreateWindow(CREATESTRUCT& cs);
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	virtual void OnInitialUpdate(); // called first time after construct
	virtual BOOL OnPreparePrinting(CPrintInfo* pInfo);
	virtual void OnBeginPrinting(CDC* pDC, CPrintInfo* pInfo);
	virtual void OnEndPrinting(CDC* pDC, CPrintInfo* pInfo);
	virtual void OnPrint(CDC* pDC, CPrintInfo* pInfo);
	//}}AFX_VIRTUAL

// Implementation
public:
	virtual ~CElliotEngineView();
#ifdef _DEBUG
	virtual void AssertValid() const;
	virtual void Dump(CDumpContext& dc) const;
#endif

protected:
	//Start date of the data points (excluding extra leading points)
	double m_startDate;
	//End date of the data points.
	double m_endDate;
	//The resolution of the data points (in sec)
	int m_resolution;

	//The timeStamps of the data points. It can include data points that are before the
	//startDate (extra leading points) to facilitate moving averages computation.
	int m_noOfPoints;
  int m_leadingExtraPoints;
  int m_offsetIntoRawArrays;

  int m_noOfRawPoints;
	double *m_timeStamps;
	double *m_volData;		//The volume values.
	double *m_highData;		//The high values.
	double *m_lowData;		//The low values.
	double *m_openData;		//The open values.
	double *m_closeData;	//The close values.

	int m_avgPeriod1;
	int m_avgPeriod2;

  virtual void ReloadRawData();
	virtual void GetData(int requestedDuration, int requestedExtraPoints);
	virtual void UpdateChart(CChartViewer *viewer);

// Generated message map functions
protected:
	//{{AFX_MSG(CElliotEngineView)
	afx_msg void OnSize(UINT nType, int cx, int cy);
	afx_msg void OnSelectChange();
	afx_msg void OnTextChange();
	afx_msg void OnSelchangeChartsize();
	afx_msg void OnHScroll(UINT nSBCode, UINT nPos, CScrollBar* pScrollBar);
	afx_msg void OnMouseMove(UINT nFlags, CPoint point);
	afx_msg void OnResolutionChange();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()

  int DrawWave(const ETime& startDate, double startPrice, const ETime& endDate, double endPrice, double* pts);
  int AddMonoWaves(XYChart* pMainChart);

};

#ifndef _DEBUG  // debug version in ElliotEngineView.cpp
inline CElliotEngineDoc* CElliotEngineView::GetDocument()
   { return (CElliotEngineDoc*)m_pDocument; }
#endif

/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_ELLIOTENGINEVIEW_H__6022A139_5151_45DC_95EB_202FEBC1912E__INCLUDED_)
