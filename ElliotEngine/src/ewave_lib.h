// ewave_lib.h
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
	\file   ewave_lib.h
	\brief  Elliot Wave Engine 
	\author Ray Rope <sendyourdollars@hotmail.com>, Johan Sörensen <johanps@users.sourceforge.net >
*/

#if !defined(ewave_lib_h)
#define ewave_lib_h

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

/////////////////////////////////////////////////////////////////////////////
// Imported procedures, i.e. implemented outside ewave_lib, but needed from within it!

#include "Etime.h"


/////////////////////////////////////////////////////////////////////////////
// Exported types and constants

#include <vector>
#include <list>
#include <map>
#include <set>
typedef unsigned char uint8;

#define UP                      10
#define DOWN                     9 
#define NEUTRAL                  8 
#define M_END_DOT                7     /* M(x) Start Point or M(x) End Point */ 


struct PriceNode
{
  // these are the members that are actually used by the ewave_lib for creating monowaves etc.
  float      price;                   // in case of high-low input data, make this the mean of high and low, otherwise make it same as "close"
  ETime      date;

  // these members are here for plotting etc outside ewave_lib.
  float      open;
  float      high;
  float      low;
  float      close;
  float      volume;

  PriceNode() {}
  void clear() { date = 0; price = open = high = low = close = volume = 0.0f; }
};

typedef std::vector<PriceNode> PriceNodeVec;


struct WaveNode
{
  const PriceNodeVec* mpPriceNodeVec;
  int mStartIndex;          // in the PriceNode array
  int mEndIndex;            // in the PriceNode array

  float mM2Retracement;
  float mM0Retracement;
  uint8 mRetracementRule;   // Rule 1-7
  char  mCondition;         // condition 'a' through 'f' (depending on the rule)
  uint8 mCategory;          // only relevant/valid for Rule 4

  // for algorithm verification purposes, and visualization
  int m0StartIndex;         // in the PriceNode array
  int m2EndIndex;           // in the PriceNode array

  // structure label        // :3 or :5
  // position indicator     // c, F, L, s, sL

  WaveNode(const PriceNodeVec* p, int s, int e) 
    : mpPriceNodeVec(p), mStartIndex(s), mEndIndex(e)
    , mM2Retracement(0.0f), mM0Retracement(0.0f)
    , mRetracementRule(0), mCondition('-'), mCategory(0)
    , m0StartIndex(-1), m2EndIndex(-1)
  { }

  WaveNode() 
    : mpPriceNodeVec(NULL), mStartIndex(-1), mEndIndex(-1)
    , mM2Retracement(0.0f), mM0Retracement(0.0f)
    , mRetracementRule(0), mCondition('-'), mCategory(0)
    , m0StartIndex(-1), m2EndIndex(-1)
  { }

  float StartPrice() const
  { return mpPriceNodeVec->at(mStartIndex).price; }

  float EndPrice() const
  { return mpPriceNodeVec->at(mEndIndex).price; }
  
  const ETime& StartDate() const
  { return mpPriceNodeVec->at(mStartIndex).date; }

  const ETime& EndDate() const
  { return mpPriceNodeVec->at(mEndIndex).date; }

  float LengthInPrice() const
  { return EndPrice() - StartPrice(); }

  int LengthInTime(int precision = DAYSECONDS) const
  { return EndDate().Diff(StartDate(), precision); }
};


typedef std::vector<WaveNode> WaveVector;


class PolyWaveVec : public WaveVector
{
public:
  PolyWaveVec(const PriceNodeVec& priceNodes)
    : m_PriceNodes(priceNodes)
  {  }

  const PriceNodeVec& m_PriceNodes;
};

/////////////////////////////////////////////////////////////////////////////
// Exported procedures

WaveVector::size_type EW_BuildMonoWaves(const PriceNodeVec& priceNodes, WaveVector& monowaves);

bool EW_FindM2(const PolyWaveVec& waves, const WaveNode& M1, int m1, WaveNode& M2);
bool EW_FindM0(const PolyWaveVec& waves, const WaveNode& M1, int m1, WaveNode& M0);
void EW_ProcessRulesOfRetracement(PolyWaveVec& waves);

int EW_MergeDataIntoPeriods(const PriceNodeVec& inVec, int interval, int valuesPerPeriod, PriceNodeVec& outVec, std::list<int>* pAmbiguities = NULL);
int EW_GetAveragePeriod(const PriceNodeVec& vec);

/////////////////////////////////////////////////////////////////////////////
// Experimental procedures

int EW_FindSimilarWaveSequences(const PolyWaveVec& waves, int m1, std::map<int, int>& matches);

#endif // !defined(ewave_lib_h)
