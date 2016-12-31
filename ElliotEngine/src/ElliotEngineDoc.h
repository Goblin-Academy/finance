// ElliotEngineDoc.h : interface of the CElliotEngineDoc class
//
/////////////////////////////////////////////////////////////////////////////
/*
 *  Implementation Of Glen Neely-Mastering Elliot Wave 
 * 
 *  This library is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU Lesser General Public
 *  License as published by the Free Software Foundation; either
 *  version 2.1 of the License, or (at your option) any later version.
 *  
 *  This library is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *  Lesser General Public License for more details.
 *  
 *  You should have received a copy of the GNU Lesser General Public
 *  License along with this library; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

/*!
	\file   ElliotEngineDoc.h
	\brief  Elliot Wave Engine 
	\author Ray Rope <sendyourdollars@hotmail.com>
	\note   Input Massaged Date .CVS See Sample dow100802.csv  
	\note   Output MonoWaveFile.txt
*/

#if !defined(AFX_ELLIOTENGINEDOC_H__141BC6A8_DE1B_4938_8B02_E1151BE705CD__INCLUDED_)
#define AFX_ELLIOTENGINEDOC_H__141BC6A8_DE1B_4938_8B02_E1151BE705CD__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#include "ewave_lib.h"

class CElliotEngineDoc //: public CDocument
{
protected: // create from serialization only
	CElliotEngineDoc();
	DECLARE_DYNCREATE(CElliotEngineDoc)
	int OnOpenDocument(LPCTSTR lpszPathName);

// Attributes
public:
  CString       m_InstrumentName;
  PriceNodeVec  m_PriceNodesRaw;
  int           m_PriceNodeIntervalRaw;   // in seconds

  PriceNodeVec  m_PriceNodes;
  int           m_PriceNodeInterval;      // in seconds, typical values can be from 30 minutes, 60 minutes etc., then days, weeks, months
  int           m_PriceNodesPerInterval;  // only valid values: 1 or 2

  PolyWaveVec   m_MonoWaves;

// Operations
public:

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CElliotEngineDoc)
	public:
	virtual bool OnNewDocument();
	virtual void Serialize(CArchive& ar);
	virtual void SetPathName(LPCTSTR lpszPathName, BOOL bAddToMRU = TRUE);
	//}}AFX_VIRTUAL

// Implementation
public:
	virtual ~CElliotEngineDoc();
#ifdef _DEBUG
	virtual void AssertValid() const;
	virtual void Dump(CDumpContext& dc) const;
#endif

protected:

  void ImportFile(CFile* fp);
  void ExportFile(CFile* fp, const char* isin);
  bool ParseBufferTicker(char * parsebuffer,DWORD fileLength);
  bool WriteMonoWaves();

// Generated message map functions
protected:
	//{{AFX_MSG(CElliotEngineDoc)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_ELLIOTENGINEDOC_H__141BC6A8_DE1B_4938_8B02_E1151BE705CD__INCLUDED_)
