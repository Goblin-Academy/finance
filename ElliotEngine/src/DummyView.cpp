// ElliotEngineView.cpp : implementation of the CElliotEngineView class
//

#include "stdafx.h"
#include "ElliotEngine.h"

#include "ElliotEngineDoc.h"
#include "DummyView.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CElliotEngineView

IMPLEMENT_DYNCREATE(CElliotEngineView, CView)

BEGIN_MESSAGE_MAP(CElliotEngineView, CView)
	//{{AFX_MSG_MAP(CElliotEngineView)
		// NOTE - the ClassWizard will add and remove mapping macros here.
		//    DO NOT EDIT what you see in these blocks of generated code!
	//}}AFX_MSG_MAP
	// Standard printing commands
	ON_COMMAND(ID_FILE_PRINT, CView::OnFilePrint)
	ON_COMMAND(ID_FILE_PRINT_DIRECT, CView::OnFilePrint)
	ON_COMMAND(ID_FILE_PRINT_PREVIEW, CView::OnFilePrintPreview)
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CElliotEngineView construction/destruction

CElliotEngineView::CElliotEngineView()
{
	// TODO: add construction code here

}

CElliotEngineView::~CElliotEngineView()
{
}

BOOL CElliotEngineView::PreCreateWindow(CREATESTRUCT& cs)
{
	// TODO: Modify the Window class or styles here by modifying
	//  the CREATESTRUCT cs

	return CView::PreCreateWindow(cs);
}

/////////////////////////////////////////////////////////////////////////////
// CElliotEngineView drawing

void CElliotEngineView::OnDraw(CDC* pDC)
{
	CElliotEngineDoc* pDoc = GetDocument();
	ASSERT_VALID(pDoc);
	// TODO: add draw code for native data here
}

/////////////////////////////////////////////////////////////////////////////
// CElliotEngineView printing

BOOL CElliotEngineView::OnPreparePrinting(CPrintInfo* pInfo)
{
	// default preparation
	return DoPreparePrinting(pInfo);
}

void CElliotEngineView::OnBeginPrinting(CDC* /*pDC*/, CPrintInfo* /*pInfo*/)
{
	// TODO: add extra initialization before printing
}

void CElliotEngineView::OnEndPrinting(CDC* /*pDC*/, CPrintInfo* /*pInfo*/)
{
	// TODO: add cleanup after printing
}

/////////////////////////////////////////////////////////////////////////////
// CElliotEngineView diagnostics

#ifdef _DEBUG
void CElliotEngineView::AssertValid() const
{
	CView::AssertValid();
}

void CElliotEngineView::Dump(CDumpContext& dc) const
{
	CView::Dump(dc);
}

CElliotEngineDoc* CElliotEngineView::GetDocument() // non-debug version is inline
{
	ASSERT(m_pDocument->IsKindOf(RUNTIME_CLASS(CElliotEngineDoc)));
	return (CElliotEngineDoc*)m_pDocument;
}
#endif //_DEBUG

/////////////////////////////////////////////////////////////////////////////
// CElliotEngineView message handlers
