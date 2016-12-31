// ElliotEngineDoc.cpp : implementation of the CElliotEngineDoc class
//

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
	\file   ElliotEngineDoc.cpp
	\brief  Elliot Wave Engine 
	\author Ray Rope <sendyourdollars@hotmail.com>, , Johan Sörensen <johanps@users.sourceforge.net>
	\note   Input Massaged Date .CVS See Sample dow100802.csv  
	\note   Output MonoWaveFile.txt
*/


//#include "stdafx.h"
//#include "ElliotEngine.h"
#include "ElliotEngineDoc.h"

#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <io.h>
#include <stdio.h>

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif
static const CString sFileDate = __TIMESTAMP__;


/////////////////////////////////////////////////////////////////////////////
// CElliotEngineDoc

IMPLEMENT_DYNCREATE(CElliotEngineDoc, CDocument)

BEGIN_MESSAGE_MAP(CElliotEngineDoc, CDocument)
	//{{AFX_MSG_MAP(CElliotEngineDoc)
		// NOTE - the ClassWizard will add and remove mapping macros here.
		//    DO NOT EDIT what you see in these blocks of generated code!
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CElliotEngineDoc construction/destruction

CElliotEngineDoc::CElliotEngineDoc()
  : m_MonoWaves(m_PriceNodes)
  , m_PriceNodeInterval(0)
  , m_PriceNodesPerInterval(1)
  , m_PriceNodeIntervalRaw(0)
{
  m_PriceNodesRaw.reserve(20000);
  m_PriceNodes.reserve(20000);
}

CElliotEngineDoc::~CElliotEngineDoc()
{
}

bool CElliotEngineDoc::OnNewDocument()
{
	if (!CDocument::OnNewDocument())
		return FALSE;

	// TODO: add reinitialization code here
	// (SDI documents will reuse this document)

	return TRUE;
}


bool CElliotEngineDoc::OnOpenDocument (LPCTSTR lpszPathName)
{
  if (!CDocument::OnOpenDocument (lpszPathName))
    return FALSE;

  SetPathName(lpszPathName, FALSE);
  m_InstrumentName = GetTitle();
  int n = m_InstrumentName.ReverseFind('.');
  if (n >= 0)
    m_InstrumentName = m_InstrumentName.Left(n);
  
  // Initialize members of the document object that 
  // aren't initialized when the document is 
  // serialized from disk...
  if (m_MonoWaves.size() == 0)
  {
#ifdef _DEBUG
    ETime t1;
    ETime t2;
    t1.Change(2006, 7, 28, 17, 0, 0);
    t2.Change(2006, 7, 31, 9, 5, 0);
    int d1 = t1.Diff(t2, 1, WEEKDAY_ONLY);
    int d2 = t2.Diff(t1, 1, WEEKDAY_ONLY);
    d1 = t1.Diff(t2, 1);
    d2 = t2.Diff(t1, 1);
    d1 = t1.Diff(t2);
    d2 = t2.Diff(t1);
#endif
    m_PriceNodeIntervalRaw = EW_GetAveragePeriod(m_PriceNodesRaw);
    // TODO: give the user more control over how to process the raw input data
    // for now use some simple heuristics
    m_PriceNodeInterval = DAYSECONDS;
    if (m_PriceNodeIntervalRaw < 3600)
    {
      m_PriceNodesPerInterval = 2;
      EW_MergeDataIntoPeriods(m_PriceNodesRaw, m_PriceNodeInterval, m_PriceNodesPerInterval, m_PriceNodes);
    }
    else
    {
      m_PriceNodes = m_PriceNodesRaw;
      m_PriceNodesRaw.clear();
    }

    EW_BuildMonoWaves(m_PriceNodes, m_MonoWaves);
    // WriteMonoWaves();
    EW_ProcessRulesOfRetracement(m_MonoWaves);
    // Write Out The MonoWaveArray To A File
    WriteMonoWaves();
  }
  return TRUE;
}

/////////////////////////////////////////////////////////////////////////////
// CElliotEngineDoc serialization

static CString RemoveSuffix(CString& s)
{
  CString f;
  int n = s.ReverseFind('.');
  if (n >= 0)
  {
    f = s.Mid(n+1);
    f.MakeLower();
    s.Delete(n+1, s.GetLength()-n-1);
  }
  return f;
}

void CElliotEngineDoc::SetPathName(LPCTSTR lpszPathName, bool bAddToMRU) 
{
  CString p = lpszPathName;
  CString s = RemoveSuffix(p);
  p += "eea";
	CDocument::SetPathName(p, bAddToMRU);
}

void CElliotEngineDoc::Serialize(CArchive& ar)
{
  int n;
  CString s, x;
	if (ar.IsStoring())
	{
    s = ar.GetFile()->GetFileTitle();
    x = RemoveSuffix(s);
    if (x != "eea")
    {
      ar.Flush();
      ExportFile(ar.GetFile(), m_InstrumentName);
    }
    else
    {
      ar << sFileDate;
      n = m_PriceNodesRaw.size();
      ar << n;
      ar << m_PriceNodeIntervalRaw;
      if (n > 0)
        ar.Write(&m_PriceNodesRaw[0], sizeof(PriceNode) * n);

      n = m_PriceNodes.size();
      ar << n;
      ar << m_PriceNodeInterval;
      ar << m_PriceNodesPerInterval;
      ar.Write(&m_PriceNodes[0], sizeof(PriceNode) * n);

      n = m_MonoWaves.size();
      ar << n;
      ar.Write(&m_MonoWaves[0], sizeof(WaveNode) * n);
    }
	}
	else  // not storing; read file
	{
    s = ar.GetFile()->GetFileTitle();
    x = RemoveSuffix(s);
    if (x != "eea")
    {
      ar.Flush();
      ImportFile(ar.GetFile());
    }
    else
    {
      ar >> s;
      if (s != sFileDate)
        throw new CArchiveException(CArchiveException::badSchema, ar.GetFile()->GetFilePath());

      ar >> n;
      ar >> m_PriceNodeIntervalRaw;
      if (n > 0)
      {
        m_PriceNodesRaw.resize(n);
        ar.Read(&m_PriceNodesRaw[0], sizeof(PriceNode) * n);
      }

      ar >> n;
      ar >> m_PriceNodeInterval;
      ar >> m_PriceNodesPerInterval;
      m_PriceNodes.resize(n);
      ar.Read(&m_PriceNodes[0], sizeof(PriceNode) * n);

      ar >> n;
      m_MonoWaves.resize(n);
      ar.Read(&m_MonoWaves[0], sizeof(WaveNode) * n);
      for (int i=0; i<n; i++)
        m_MonoWaves[i].mpPriceNodeVec = &m_PriceNodes;
    }
  }
	
	//COleDocument::Serialize(ar);
}

void CElliotEngineDoc::ImportFile(CFile* fp)
{
  size_t fileLength = fp->GetLength();
  if (fileLength > 0)
  {
    char* loadBuffer = (char*)malloc(fileLength+1);
    fp->Read(loadBuffer, fileLength);
    loadBuffer[fileLength] = '\0';

  	ParseBufferTicker(loadBuffer, fileLength);
  	free(loadBuffer);
  }
}

void CElliotEngineDoc::ExportFile(CFile* fp, const char* isin)
{
  CString s = "time;isin;high;low;last;vol$;open\r\n";
  fp->Write(s, s.GetLength());

  char buf[100];
  PriceNodeVec::const_iterator it = m_PriceNodes.begin();
  while (it != m_PriceNodes.end())
  {
    const PriceNode& n = *it++;

    sprintf(buf, "%s;%s;%g;%g;%g;%g;%g\r\n",
      n.date.Format("%Y%m%d"),
      isin,
      n.high,
      n.low,
      n.price,
      n.volume,
      n.close );
    fp->Write(buf, strlen(buf));
  } // while
}

/////////////////////////////////////////////////////////////////////////////
// CElliotEngineDoc diagnostics

#ifdef _DEBUG
void CElliotEngineDoc::AssertValid() const
{
	CDocument::AssertValid();
}

void CElliotEngineDoc::Dump(CDumpContext& dc) const
{
	CDocument::Dump(dc);
}
#endif //_DEBUG

/////////////////////////////////////////////////////////////////////////////
// CElliotEngineDoc commands


typedef enum {Invalid,Date,Open,High,Low,Close,Volume,Ignore} tFields;

static int ParseLineIntoNode(char* pLine, char delimiter, const tFields* pLineTemplate, const char* pDateTemplate, PriceNode& node)
{
  char* pFields[20] = {NULL};
  char* p = pLine;

  int numFields = 0;
  pFields[numFields++] = pLine;
  for (; *p; p++)
  {
    if (*p == delimiter)
    {
      *p = NULL;
      pFields[numFields++] = p+1;
    }
  }

  int d, i;
  for (i=0; i<numFields && pLineTemplate[i] != Invalid; i++)
  {
    switch (pLineTemplate[i])
    {
    case Date:
      if (!node.date.Unformat(pFields[i], pDateTemplate))
        return 0;
      d = node.date.GetDayOfWeek();
#ifdef _DEBUG
      if (d < 1 || d > 5)
        TRACE("Found non week-day date at %s\n", pFields[i]);
#endif
      break;
    case Open:
      node.open   = atof(pFields[i]);
      break;
    case High:
      node.high   = atof(pFields[i]);
      break;
    case Low:
      node.low    = atof(pFields[i]);
      break;
    case Close:
      node.close  = atof(pFields[i]);
      break;
    case Volume:
      node.volume = atof(pFields[i]);
      break;
    }
  }
  return i;
}

const tFields YahooTemplate[]     = { Date,Open,High,Low,Close,Volume, Invalid };
const char YahooDateTemplate1[]   = "%d-%b-%y";
const char YahooDateTemplate2[]   = "%m/%d/%y";
const tFields HK_DayTemplate[]    = { Date,Ignore,High,Low,Close,Volume,Ignore,Open, Invalid };
const char HK_DateTemplateDay[]   = "%Y%m%d";
const tFields HK_IntraTemplate[]  = { Date,Ignore,High,Low,Close,Volume, Invalid };
const char HK_DateTemplateIntra[] = "%Y%m%d%H%M";


bool CElliotEngineDoc::ParseBufferTicker(char * parsebuffer, DWORD fileLength)
{
  PriceNodeVec tempNodes;         // if infile is sorted in the wrong order
  PriceNode Node;
  DWORD fileindex = 0;

  // skip first header line
  while(parsebuffer[fileindex] != 0x0a)
    fileindex++;
  parsebuffer[fileindex++] = '\0';
  while(iswspace(parsebuffer[fileindex]))
    fileindex++;

  const char* pDateTemplate = YahooDateTemplate2;
  const tFields *pLineTemplate = YahooTemplate;
  char delimiter = ',';

  enum { Yahoo1, Yahoo2, HK_DAY, HK_INTRA } FileType = Yahoo2;
  // TODO: get the line field template from the first header line in the input file
  if (strstr(parsebuffer, "Close*") != NULL)      // current format returned from Yahoo?
  {
    FileType = Yahoo1;
    pDateTemplate = YahooDateTemplate1;
  }
  else
  if (strstr(parsebuffer, "time;isin;high;low;last;vol#;vol$;open") != NULL)
  {
    FileType = HK_DAY;
    pLineTemplate = HK_DayTemplate;
    pDateTemplate = HK_DateTemplateDay;
    delimiter = ';';
  }
  else
  if (strstr(parsebuffer, "time;isin;high;low;last;vol#") != NULL)
  {
    FileType = HK_INTRA;
    pLineTemplate = HK_IntraTemplate;
    pDateTemplate = HK_DateTemplateIntra;
    delimiter = ';';
  }

  while(fileindex < fileLength)
	{
    char* pLine = &parsebuffer[fileindex];
		while(parsebuffer[fileindex] && parsebuffer[fileindex] != 0x0a && parsebuffer[fileindex] != 0x0d)
			++fileindex;
		parsebuffer[fileindex++] = '\0';
    while(iswspace(parsebuffer[fileindex]))
      fileindex++;
    Node.clear();
    if (!ParseLineIntoNode(pLine, delimiter, pLineTemplate, pDateTemplate, Node))
      continue;

    Node.price  = Node.close;
    // Node.price  = (HIGH + LOW) / 2;
    tempNodes.push_back(Node);
  } //while

  // in case the input-file was sorted in reverse order
  if (tempNodes.size() >= 2)
  {
    // check the order in the tempNode vector, to see if we need to go through it backwards or forwards
    // TODO: implement partial import/update check, so we mark the price nodes that are "new"
    //       to avoid affecting all old analysis not affected by the new data
    if (tempNodes.front().date > tempNodes.back().date)
    {
      PriceNodeVec::const_iterator it = tempNodes.end();
      while (it != tempNodes.begin())
        m_PriceNodesRaw.push_back(*(--it));
    }
    else
    {
      PriceNodeVec::const_iterator it = tempNodes.begin();
      while (it != tempNodes.end())
        m_PriceNodesRaw.push_back(*(it++));
    }
  }
  return TRUE;
}


bool CElliotEngineDoc::WriteMonoWaves()
{
  FILE * DosStream;
  float  startPrice;
  float  endPrice;

  CString s = GetPathName();
  RemoveSuffix(s);
  s += "monowaves.txt";
  DosStream = fopen(s,"w+");
  fprintf(DosStream,"Startdate Nodes             prices           m0start    m2end  RetracementRule,Condition(,category)\n");

  for (int n=0; n < m_MonoWaves.size(); n++)
  {
    startPrice = m_MonoWaves[n].StartPrice();
    endPrice   = m_MonoWaves[n].EndPrice();

    fprintf(DosStream,"%08d  %6d - %6d   %5.2f - %5.2f   %6d / %6d  %d %c (%d)\n",
            m_MonoWaves[n].StartDate().GetYMD(),
            m_MonoWaves[n].mStartIndex,
            m_MonoWaves[n].mEndIndex,
            startPrice,
            endPrice,
            m_MonoWaves[n].m0StartIndex,
            m_MonoWaves[n].m2EndIndex,
       (int)m_MonoWaves[n].mRetracementRule,
            m_MonoWaves[n].mCondition,
       (int)m_MonoWaves[n].mCategory   );
  }
	  
  fclose(DosStream);
#ifdef NO_CHART
  AfxMessageBox("An output file has been produced: \n" + s);
#endif
  return TRUE;
}
