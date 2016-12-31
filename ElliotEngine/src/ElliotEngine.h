// ElliotEngine.h : main header file for the ELLIOTENGINE application
//

#if !defined(AFX_ELLIOTENGINE_H__EA6639D3_EEF9_4F19_806A_4160107A5D75__INCLUDED_)
#define AFX_ELLIOTENGINE_H__EA6639D3_EEF9_4F19_806A_4160107A5D75__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

//#ifndef __AFXWIN_H__
//#error include 'stdafx.h' before including this file for PCH
//#endif

#include "Resource.h"       // main symbols

/////////////////////////////////////////////////////////////////////////////
// CElliotEngineApp:
// See ElliotEngine.cpp for the implementation of this class
//

class CElliotEngineApp //: public CWinApp
{
public:
	CElliotEngineApp();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CElliotEngineApp)
	public:
	virtual bool InitInstance();
	//}}AFX_VIRTUAL

// Implementation
	//{{AFX_MSG(CElliotEngineApp)
	afx_msg void OnAppAbout();
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_ELLIOTENGINE_H__EA6639D3_EEF9_4F19_806A_4160107A5D75__INCLUDED_)
