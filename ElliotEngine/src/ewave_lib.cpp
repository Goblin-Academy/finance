// ewave_lib.cpp
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
	\file   ewave_lib.cpp
	\brief  Elliot Wave Engine 
	\author Ray Rope <sendyourdollars@hotmail.com>, Johan Sörensen <johanps@users.sourceforge.net>
*/

#include <stdafx.h>
#include <stdio.h>
#include <math.h>
#include <float.h>
#include "ewave_lib.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif


const float phi = 0.618033989f;
const float phi_precision = phi * 0.02f;


/////////////////////////////////////////////////////////////////////////////


WaveVector::size_type EW_BuildMonoWaves(const PriceNodeVec& pricenodes, WaveVector& monowaves)
{
  const int num_nodes = pricenodes.size();
  int start = 0;
  int in_index = 1;
  float direction;        // >0 means up, <0 means down
  float next_dir;

  if (num_nodes < 2)
    return 0;

  // the first monowave starts at our first data point
  direction = (pricenodes[1].price - pricenodes[0].price);

  while (in_index < num_nodes)
  {
    // find out where the current monowave ends
    while (in_index < num_nodes - 1)
    {
      next_dir = (pricenodes[in_index+1].price - pricenodes[in_index].price);
      if (direction * next_dir < 0.0f)
        break;
      in_index++;
    }
    
    monowaves.push_back(WaveNode(&pricenodes, start, in_index));
    direction = next_dir;
    start = in_index++;
  } // while

  return monowaves.size();
}


/////////////////////////////////////////////////////////////////////////////

static int longest_m0_index = -1;
static int longest_m0_size = 1;
static int longest_m2_index = -1;
static int longest_m2_size = 1;


// Given "M1", find the monowave, or wave group, denoted M2
// note that when the resulting M2 is a group, it will encompass three or more waves in the input vector
bool EW_FindM2(const PolyWaveVec& waves, const WaveNode& M1, int m1, WaveNode& M2)
{
  bool bFound = false;
  float m1start = M1.StartPrice();
  float m1end   = M1.EndPrice();
  float m1high  = std::max(m1start, m1end);
  float m1low   = std::min(m1start, m1end);
  float m2high = m1low;
  float m2low  = m1high;
  int extreme_low_index = -1;
  int extreme_high_index = -1;

  // note that the m1 input-parameter may be an in-exact hint as to where M1 ends,
  // we have to find the mono wave that corresponds to the wave (or group) that corresponds to M1 for the moment
  for (; m1 < waves.size(); m1++)
    if (waves[m1].mEndIndex == M1.mEndIndex)
      break;

  int i;
  for (i = m1 + 1; i < waves.size(); i++)
  {
    if (waves[i].EndPrice() > m1high || waves[i].EndPrice() < m1low)
    {
      bFound = true;
      break;
    }
    if (waves[i].EndPrice() > m2high)
      m2high = waves[i].EndPrice(), extreme_high_index = i;
    if (waves[i].EndPrice() < m2low)
      m2low = waves[i].EndPrice(), extreme_low_index = i;
  } // while

  int n = i - m1;
  if (n > 2)
  {
    // if it took more than two monowaves to get out the the m1 range,
    // then there was a turn somewhere, and the end of m2 is at the "extreme" index
    // and m2 must always consist of an odd number of monowaves
    if (((extreme_low_index - m1) %2) != 0)
      i = extreme_low_index;
    else
    if (((extreme_high_index - m1) %2) != 0)
      i = extreme_high_index;
    else
    {
      //TRACE("EW_FindM2: problem finding m2 for m1 ending at %d\n", M1.EndDate());
    }
  }
  else
  if (n == 2)
  {
    i = m1 + 1;       // m2 is confirmed complete somewhere within m1, since m3 exceeds m1 high/low
  }
  // else only remaining alternative is that m2 retraced m1 completely itself, thus i = m1 + 1

  // just for fun, keep track of where we found the most intricate m2
  n = i - m1;
  if (n > longest_m2_size)
  {
    longest_m2_size = n;
    longest_m2_index = m1;
  }
  
  // if bFound is false, then the returned M2 is only partially completed
  M2.mpPriceNodeVec = &waves.m_PriceNodes;
  M2.mStartIndex = M1.mEndIndex;
  if (i < waves.size())
    M2.mEndIndex = waves[i].mEndIndex;
  else
    M2.mEndIndex = waves.m_PriceNodes.size();
  return bFound;
}

// Given "m1", find the monowave, or wave group, denoted M0
// note that when the resulting M0 is a group, it will encompass three or more waves in the input vector
bool EW_FindM0(const PolyWaveVec& waves, const WaveNode& M1, int m1, WaveNode& M0)
{
  bool bFound = false;
  float m1start = M1.StartPrice();
  float m1end   = M1.EndPrice();
  float m1high  = std::max(m1start, m1end);
  float m1low   = std::min(m1start, m1end);
  float m0high = m1low;
  float m0low  = m1high;
  int extreme_low_index = -1;
  int extreme_high_index = -1;

  // note that the m1 input-parameter may be an in-exact hint as to where M1 begins,
  // we have to find the mono wave that corresponds to the wave (or group) that corresponds to M1 for the moment
  for (; m1 > 0; m1--)
    if (waves[m1].mStartIndex == M1.mStartIndex)
      break;

  int i;
  for (i = m1 - 1; i >= 0; i--)
  {
    if (waves[i].StartPrice() > m1high || waves[i].StartPrice() < m1low)
    {
      bFound = true;
      break;
    }
    if (waves[i].StartPrice() > m0high)
      m0high = waves[i].StartPrice(), extreme_high_index = i;
    if (waves[i].StartPrice() < m0low)
      m0low = waves[i].StartPrice(), extreme_low_index = i;
  } // while

  int n = m1 - i;
  if (n > 2)
  {
    // if it took more than two monowaves to get out the the m1 range,
    // then there was a turn somewhere, and the start of m0 is at the "extreme" index
    // and m0 must always consist of an odd number of monowaves
    if (((m1 - extreme_low_index) %2) != 0)
      i = extreme_low_index;
    else
    if (((m1 - extreme_high_index) %2) != 0)
      i = extreme_high_index;
    else
    {
      //TRACE("EW_FindM0: problem finding m0 for m1 starting at %d\n", M1.StartDate());
    }
  }
  else
  if (n == 2)
  {
    i = m1 - 1;       // m0 is confirmed complete somewhere within m1, since m-1 exceeds m1 high/low
  }
  // else only remaining alternative is that m0 retraced m1 completely itself, thus i = m1 - 1

  // just for fun, keep track of where we found the most intricate m2
  n = m1 - i;
  if (n > longest_m0_size)
  {
    longest_m0_size = n;
    longest_m0_index = m1;
  }

  M0.mpPriceNodeVec = &waves.m_PriceNodes;
  M0.mEndIndex = M1.mStartIndex;
  if (i >= 0)
    M0.mStartIndex = waves[i].mStartIndex;
  else
    M0.mStartIndex = -1;
  return bFound;
}


//
// Look at each individual monowave by itself (mentally consider it "m1"), and determine its
// relationship with neighbouring monowaves (or monowave groups) "m0" and "m2" to determine 
// which Retracement Rule should be applied
//
void EW_ProcessRulesOfRetracement(PolyWaveVec& waves)
{
  WaveNode M0(&waves.m_PriceNodes, 0, 0);
  WaveNode M2(&waves.m_PriceNodes, 0, 0);
  WaveNode M3(&waves.m_PriceNodes, 0, 0);
  float m3retracement;

  if (waves.size() < 2)
    return;

  longest_m0_index = -1;
  longest_m0_size = 1;
  longest_m2_index = -1;
  longest_m2_size = 1;

  for (int m1 = 0; m1 < waves.size(); m1++)
  {
    if (EW_FindM0(waves, waves[m1], m1, M0))
      waves[m1].m0StartIndex = M0.mStartIndex;
    if (EW_FindM2(waves, waves[m1], m1, M2))
      waves[m1].m2EndIndex = M2.mEndIndex;

    waves[m1].mM0Retracement = 0.0f;
    waves[m1].mM2Retracement = 0.0f;

    if (M2.mEndIndex < waves.m_PriceNodes.size())
    {
      waves[m1].mM2Retracement = fabs(M2.LengthInPrice() / waves[m1].LengthInPrice());
      if (waves[m1].mM2Retracement < (1.0f - phi))
        waves[m1].mRetracementRule = 1;
      else
      if (waves[m1].mM2Retracement < (phi - phi_precision))
        waves[m1].mRetracementRule = 2;
      else
      if (waves[m1].mM2Retracement < (phi + phi_precision))
        waves[m1].mRetracementRule = 3;
      else
      if (waves[m1].mM2Retracement < 1.0f)
        waves[m1].mRetracementRule = 4;
      else
      if (waves[m1].mM2Retracement < (1.0f + phi))
        waves[m1].mRetracementRule = 5;
      else
      if (waves[m1].mM2Retracement <= (2.0f + phi))
        waves[m1].mRetracementRule = 6;
      else
        waves[m1].mRetracementRule = 7;
    }

    if (M0.mStartIndex >= 0)
    {
      waves[m1].mM0Retracement = fabs(M0.LengthInPrice() / waves[m1].LengthInPrice());
      switch (waves[m1].mRetracementRule)
      {
        case 1:
          if (waves[m1].mM0Retracement < phi)
            waves[m1].mCondition = 'a';
          else
          if (waves[m1].mM0Retracement < 1.0f)
            waves[m1].mCondition = 'b';
          else
          if (waves[m1].mM0Retracement < (1.0f + phi))
            waves[m1].mCondition = 'c';
          else
            waves[m1].mCondition = 'd';
          break;

        case 2:
          if (waves[m1].mM0Retracement < (1.0f - phi))
            waves[m1].mCondition = 'a';
          else
          if (waves[m1].mM0Retracement < phi)
            waves[m1].mCondition = 'b';
          else
          if (waves[m1].mM0Retracement < 1.0f)
            waves[m1].mCondition = 'c';
          else
          if (waves[m1].mM0Retracement <= (1.0f + phi))
            waves[m1].mCondition = 'd';
          else
            waves[m1].mCondition = 'e';
          break;

        case 3:
          if (waves[m1].mM0Retracement < (1.0f - phi))
            waves[m1].mCondition = 'a';
          else
          if (waves[m1].mM0Retracement < phi)
            waves[m1].mCondition = 'b';
          else
          if (waves[m1].mM0Retracement < 1.0f)
            waves[m1].mCondition = 'c';
          else
          if (waves[m1].mM0Retracement < (1.0f + phi))
            waves[m1].mCondition = 'd';
          else
          if (waves[m1].mM0Retracement <= (2.0f + phi))
            waves[m1].mCondition = 'e';
          else
            waves[m1].mCondition = 'f';
          break;

        case 4:
          if (waves[m1].mM0Retracement < (1.0f - phi))
            waves[m1].mCondition = 'a';
          else
          if (waves[m1].mM0Retracement < 1.0f)
            waves[m1].mCondition = 'b';
          else
          if (waves[m1].mM0Retracement < (1.0f + phi))
            waves[m1].mCondition = 'c';
          else
          if (waves[m1].mM0Retracement <= (2.0f + phi))
            waves[m1].mCondition = 'd';
          else
            waves[m1].mCondition = 'e';
          // figure out category depending on M3!
          m3retracement = 0.0f;
          if (EW_FindM2(waves, M2, m1, M3))
            m3retracement = fabs(M3.LengthInPrice() / M2.LengthInPrice());
          if (m3retracement >= 1.0f && m3retracement < (1.0f + phi))
            waves[m1].mCategory = 1;
          else
          if (m3retracement >= (1.0f + phi) && m3retracement <= (2.0f + phi))
            waves[m1].mCategory = 2;
          else
          if (m3retracement > (2.0f + phi))
            waves[m1].mCategory = 3;
          break;

        case 5:
          if (waves[m1].mM0Retracement < 1.0f)
            waves[m1].mCondition = 'a';
          else
          if (waves[m1].mM0Retracement < (1.0f + phi))
            waves[m1].mCondition = 'b';
          else
          if (waves[m1].mM0Retracement <= (2.0f + phi))
            waves[m1].mCondition = 'c';
          else
            waves[m1].mCondition = 'd';
          break;

        case 6:
          if (waves[m1].mM0Retracement < 1.0f)
            waves[m1].mCondition = 'a';
          else
          if (waves[m1].mM0Retracement < (1.0f + phi))
            waves[m1].mCondition = 'b';
          else
          if (waves[m1].mM0Retracement <= (2.0f + phi))
            waves[m1].mCondition = 'c';
          else
            waves[m1].mCondition = 'd';
          break;

        case 7:
          if (waves[m1].mM0Retracement < 1.0f)
            waves[m1].mCondition = 'a';
          else
          if (waves[m1].mM0Retracement < (1.0f + phi))
            waves[m1].mCondition = 'b';
          else
          if (waves[m1].mM0Retracement <= (2.0f + phi))
            waves[m1].mCondition = 'c';
          else
            waves[m1].mCondition = 'd';
          break;
        // default: don't care
      } // switch
    }
  } // for

  //if (longest_m0_index > 0)
    //TRACE("longest m0 at %s : %d components\n", waves[longest_m0_index].StartDate().Format(), longest_m0_size);
  //if (longest_m2_index > 0)
    //TRACE("longest m2 at %s : %d components\n", waves[longest_m2_index].EndDate().Format(), longest_m2_size);
}


/////////////////////////////////////////////////////////////////////////////

static int ReportNewPeriod(const ETime& highDate, 
                           const ETime& lowDate, 
                                 int valuesPerPeriod,
                                 PriceNode& tempNode,     // in-out 
                                 PriceNodeVec& outVec)
{
  int newOutNodes = 0;

  if (tempNode.high == FLT_MIN)
    tempNode.high = tempNode.close;
  if (tempNode.low == FLT_MAX)
    tempNode.low = tempNode.close;

  if (valuesPerPeriod != 2)
  { // report one value per period, either mean of high-low, or close
    if (valuesPerPeriod == 1)
      tempNode.price = (tempNode.low + tempNode.high) / 2.0f;
    else
      tempNode.price = tempNode.close;
    outVec.push_back(tempNode);
    newOutNodes++;
  }
  else
  { // report two values (high and low) in the order they occur within the period
    if (highDate == lowDate)
    {
      tempNode.price = (tempNode.low + tempNode.high) / 2.0f;
      outVec.push_back(tempNode);
      newOutNodes++;
      //TRACE("Ambiguous high/low at %s\n", tempNode.date.Format());
    }
    else
    {
      PriceNode tempNode2 = tempNode;
      tempNode.date = lowDate;
      tempNode.price = tempNode.open = tempNode.high = tempNode.close = tempNode.low;
      tempNode.volume /= 2.0f;
      tempNode2.date = highDate;
      tempNode2.price = tempNode2.open = tempNode2.low = tempNode2.close = tempNode2.high;
      tempNode2.volume /= 2.0f;
      if (highDate < lowDate)
      {
        outVec.push_back(tempNode2);
        outVec.push_back(tempNode);
      }
      else
      {
        outVec.push_back(tempNode);
        outVec.push_back(tempNode2);
      }
      newOutNodes += 2;
    }
  } // else, two values per period

  tempNode.clear();
  tempNode.high = FLT_MIN;
  tempNode.low = FLT_MAX;
  return newOutNodes;
}

int EW_MergeDataIntoPeriods(const PriceNodeVec& inVec, int interval, int valuesPerPeriod, PriceNodeVec& outVec, std::list<int>* pAmbiguities)
{
  const int inNodes = inVec.size();
  int newOutNodes = 0;
  PriceNodeVec::const_iterator inIt = inVec.begin();
  PriceNodeVec::iterator outIt = outVec.begin();
  ETime oldDate = 0;
  ETime date, highDate, lowDate;
  PriceNode tempNode;

  tempNode.clear();
  tempNode.high = FLT_MIN;
  tempNode.low = FLT_MAX;

  for (; inIt != inVec.end(); inIt++)
  {
    const PriceNode& inNode = (*inIt);
    date = inNode.date;
    if (oldDate == 0)
      oldDate = date;

    bool bNewPeriod = false;
    if (interval < DAYSECONDS)
      bNewPeriod = (oldDate.GetSecondsWithinDay() / interval) != (date.GetSecondsWithinDay() / interval); // consolidate to intraday periods (e.g. hour)
    else
    if (interval == DAYSECONDS)
      bNewPeriod = (oldDate.GetDay() != date.GetDay());             // consolidate to days
    else
    if (interval == WEEKSECONDS)
      bNewPeriod = (date.GetDayOfWeek() < oldDate.GetDayOfWeek());  // consolidate to weeks
    else
    // if (interval == MONTHSECONDS)
      bNewPeriod = (oldDate.GetMonth() != date.GetMonth());         // consolidate to months

    if (bNewPeriod)
    {
      tempNode.date = oldDate;
      int n = ReportNewPeriod(highDate, lowDate, valuesPerPeriod, tempNode, outVec);
      newOutNodes += n;
      if (n < 2 && valuesPerPeriod == 2 && pAmbiguities)
        pAmbiguities->push_back(newOutNodes);
    } // if bNewPeriod

    //update period high low last and volume
    if ((inNode.high > tempNode.high) && (inNode.high > 0.0f))
      tempNode.high = inNode.high, highDate = date;
    else
    if ((inNode.close > tempNode.high) && (inNode.close > 0.0f))
      tempNode.high = inNode.close, highDate = date;

    if ((inNode.low < tempNode.low) && (inNode.low > 0.0f))
      tempNode.low = inNode.low, lowDate = date;
    else
    if ((inNode.close < tempNode.low) && (inNode.close > 0.0f))
      tempNode.low = inNode.close, lowDate = date;

    if (inNode.close > 0.0f)
      tempNode.close = inNode.close;
    tempNode.volume += inNode.volume;

    if (tempNode.open == 0.0f)
    {
      if (inNode.open != 0.0f)
        tempNode.open = inNode.open;
      else
      // this is a bit wrong, but if there's no open values in the indata, this is better than nothing; better the more fine-grained the indata is
      if (inNode.close != 0.0f)
        tempNode.open = inNode.close;
    }
    oldDate = date;
  } // while

  // was there an unfinished period?
  if (tempNode.close > 0.0f)
  {
    tempNode.date = oldDate;
    int n = ReportNewPeriod(highDate, lowDate, valuesPerPeriod, tempNode, outVec);
    newOutNodes += n;
    if (n < 2 && valuesPerPeriod == 2 && pAmbiguities)
      pAmbiguities->push_back(newOutNodes);
  }

  return newOutNodes;
}


int EW_GetAveragePeriod(const PriceNodeVec& vec)
{
  if (vec.size() < 2)
    return 0;

  double sum = 0.0;
  PriceNodeVec::const_iterator it = vec.begin();
  ETime t = (*it++).date;
  for (; it != vec.end(); it++)
  {
    sum += (*it).date.Diff(t, 1, WEEKDAY_ONLY);
    t = (*it).date;
  }

  return (int)(sum / (vec.size() - 1));
}


/////////////////////////////////////////////////////////////////////////////
// Experimental procedures

std::pair<int, int>
EW_FindSimilarWaveSequence(const PolyWaveVec& waves, int m1, int& startIndex, int lengthThreshold, float qmax)
{
  PolyWaveVec m1cache(waves.m_PriceNodes);    // this stores M1, M0, M-1, M-2 etc (in reverse order)
  std::pair<int, int> IndexAndLength(0, 0);
  int len;
  float qmin = 1.0f / qmax;

  // populate the cache containing the M0, M-1, M-2 etc sequence we're looking for
  WaveNode M1 = waves[m1];
  m1cache.push_back(waves[m1]);
  WaveNode& M1ref = m1cache[0];
  for (int i=0; i<10; i++)
  {
    WaveNode M0;
    if (EW_FindM0(waves, M1, m1, M0))
    {
      M1ref.mM0Retracement = fabs(M0.LengthInPrice() / M1ref.LengthInPrice());
      m1cache.push_back(M0);
      M1ref = m1cache[ m1cache.size()-1 ];
    }
    else
      break;
    M1 = M0;
  }

  do
  {
    if (startIndex == m1)
      continue;
    if (waves[startIndex].LengthInPrice() * waves[m1].LengthInPrice() < 0.0f)
      continue;   // not looking at a wave in the same direction

    float q = 9999.0f;
    len = 0;
    WaveNode Mc1 = waves[startIndex];
    WaveNode Mc0;
    if (EW_FindM0(waves, Mc1, startIndex, Mc0))
    {
      Mc1.mM0Retracement = fabs(Mc0.LengthInPrice() / Mc1.LengthInPrice());
      q = fabs(log10(Mc1.mM0Retracement) - log10(m1cache[len].mM0Retracement));
    }
    else break;

    while ((startIndex-len) >= 0 && (q <= qmax))
//    while ((startIndex-len) >= 0 && waves[startIndex-len].mRetracementRule == waves[m1-len].mRetracementRule)
    {
      len++;
      Mc1 = Mc0;
      if (EW_FindM0(waves, Mc1, startIndex, Mc0)) // it's ok to supply the "wrong" startindex; it's just used as searching start anyway
      {
        Mc1.mM0Retracement = fabs(Mc0.LengthInPrice() / Mc1.LengthInPrice());
        q = fabs(log10(Mc1.mM0Retracement) - log10(m1cache[len].mM0Retracement));
      }
      else
        break;
    }

    if (len >= lengthThreshold)
    {
      startIndex -= len;
      //TRACE("EW_FindMatchingWaveSequence: found match for m1=%d, len %d at %d\n", m1, len, startIndex);
      break;
    }
  } while (--startIndex > 0);

  return std::pair<int, int>(startIndex, len);
}


int EW_FindSimilarWaveSequences(const PolyWaveVec& waves, int m1, std::map<int, int>& matches)
{
  std::map<int, int> sizes;
  int startIndex = waves.size() - 1;
  int numMatches = 0;
  int lengthThreshold = 3;
  float qmax = 0.2f; // sqrt(2.0);
  while (startIndex > 0)
  {
    std::pair<int, int> IndexAndLength = EW_FindSimilarWaveSequence(waves, m1, startIndex, lengthThreshold, qmax);
    startIndex--;
    if (IndexAndLength.second >= lengthThreshold)
    {
      numMatches++;
      matches.insert(IndexAndLength);
      sizes[IndexAndLength.second] += 1;
    }
  }

  while (numMatches > 10 && sizes.size() > 0)
  {
    int smallestMatch = (*sizes.begin()).first;
    sizes.erase(sizes.begin());

    std::map<int, int>::iterator it = matches.begin();
    while (it != matches.end() && numMatches > 10)
    {
      if ((*it).second <= smallestMatch)
      {
        it = matches.erase(it);
        numMatches--;
      }
      else 
        it++;
    }
  }

  return numMatches;
}

