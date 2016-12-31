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
	\file   ETime.cpp
	\brief  Elliot Wave Engine 
	\author Johan Sörensen <johanps@users.sourceforge.net>
*/

#include <stdafx.h>
#include <stdio.h>
#include <iostream>
#include <math.h>
#include <stdlib.h>
#include "ETime.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif


// Class ETime 
/*static*/int ETime::m_TradingDayOpen  = 32400; // 09:00, in seconds from start-of-day
/*static*/int ETime::m_TradingDayClose = 63000; // 17:30, in seconds from start-of-day
/*static*/int ETime::m_BreakYear_1900_2000 = 10;     // if a two-digit year value is above this, then it's the 1900's, otherwise the 2000's


/*static*/ bool ETime::IsLeapYear(int y)
{
  // from http://mathforum.org/dr.math/faq/faq.calendar.html
  // Every fourth year is a leap year. 2004, 2008, and 2012 are leap years. 
  // However, every hundredth year is not a leap year. 1900 and 2100 are not leap years. 
  // Every four hundred years, there's a leap year after all. 2000 and 2400 are leap years. 

  bool bIsLeapYear = ((y % 4) == 0);
  if (bIsLeapYear)
  {
    if ((y % 100) == 0)
      if ((y % 400) != 0)
        bIsLeapYear = false;
  }
  return bIsLeapYear;
}


bool ETime::IsEOD () const
{
  unsigned long withinDay = (unsigned long)(m_Value % (__int64_t)1000000);
  return withinDay == 235959;
}

double ETime::GetJulianDate() const
{
  unsigned long YMD = (unsigned long)(m_Value / (__int64_t)1000000);
  //Given the year Y, month M, and day D, if M = 1 or 2, then let 
  //y = Y-1 and m = M+12 (this considers January and February as the 
  // 13th and 14th months of the previous year).  Otherwise, let y = Y and 
  //m = M.
  int Y = YMD / 10000;
  int M = (YMD / 100) % 100;
  int D = YMD % 100;
  if (M == 1 || M == 2)
    Y--, M += 12;

  // In the Gregorian calendar (after Oct. 15, 1582), let A = Int(y/100), 
  // and B = 2 - A + Int(A/4).
  int A = Y / 100;
  int B = 2 - A + A / 4;
  double JD = floor(365.25*Y) + floor(30.6001*(M+1)) + D + B + 1720994.5;
  return JD;
}

int ETime::GetDayOfWeek() const
{
  // For mathematical background see 
  // http://mathforum.org/library/drmath/view/54374.html
  // 
  double JD = GetJulianDate();

  // To find the day of the week, add 1.5 to the Julian date 
  // calculated in step 1. Then find the REMAINDER W when (JD+1.5) is 
  // divided by 7. For example, for January 3, 1985, when we divide 2446070 
  // by 7, we get a quotient of  349438 and a remainder of 4:
  
  return (int)(JD + 1.5) % 7;
 //  0                    Sunday
 //  1                    Monday
 //  2                    Tuesday
 //  3                    Wednesday
 //  4                    Thursday
 //  5                    Friday
 //  6                    Saturday
}

int ETime::GetSecondsWithinDay() const
{
  return GetHour() * 3600 + GetMinute() * 60 + GetSecond();
}

bool ETime::SameDay (const ETime& otherTime) const
{
  return GetYMD() == otherTime.GetYMD();
}

static inline int DayBit(int dayOfWeek)
{
  return 1 << dayOfWeek;
}

int ETime::Diff(const ETime& otherTime, int precision, int dayMask) const
{
  double J = GetJulianDate();
  __int64_t JD = (__int64_t)J;
  __int64_t otherJD = (__int64_t)otherTime.GetJulianDate();
  int dir = (otherTime.m_Value < m_Value ? -1 : 1);

  if ((dayMask &0x7f) == 0x7f)         // normal calendar calculation?
  {
    if (precision == DAYSECONDS)
      return (int)(JD - otherJD);
    else
    if (precision > DAYSECONDS)
      return (int) (DAYSECONDS * (JD - otherJD) / precision);     // this may be a bit simplistic? doesn't account for "same week" or "next week", just the number of whole weeks in between

    JD *= DAYSECONDS;
    JD += GetSecondsWithinDay();
    otherJD *= DAYSECONDS;
    otherJD += otherTime.GetSecondsWithinDay();
    return (int)((JD - otherJD) / (__int64_t)precision);
  }

  int count = 0;
  J += 1.5; // day-of-week calculations are embedded below
  if (precision < DAYSECONDS)
  {
    int i = GetSecondsWithinDay();
    int j = otherTime.GetSecondsWithinDay();
    if (JD == otherJD)
      return (i - j) / precision;

    if (i >= m_TradingDayOpen && i <= m_TradingDayClose && dir > 0)
      count -= (i - m_TradingDayOpen) / precision;
    else
    if (i >= m_TradingDayOpen && i <= m_TradingDayClose && dir < 0)
      count += (m_TradingDayClose - i) / precision;

    if (j >= m_TradingDayOpen && j <= m_TradingDayClose && dir < 0)
      count -= (m_TradingDayClose - j) / precision;
    else
    if (j >= m_TradingDayOpen && j <= m_TradingDayClose && dir > 0)
      count += (j - m_TradingDayOpen) / precision;

    for (; JD != otherJD; JD += dir, J += dir)
    {
      if ((DayBit((int)J % 7) & dayMask) != 0)
        count += dir * (m_TradingDayClose - m_TradingDayOpen) / precision;
    }
  }
  else
  {
    for (; JD != otherJD; JD += dir, J += dir)
    {
      if ((DayBit((int)J % 7) & dayMask) == 0)
        count += dir * DAYSECONDS / precision;
    }
  }
  return -count;
}


static const int MonthDays[] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };

void ETime::MoveDays(int days, int dayMask)
{
  dayMask &= 0x7f;
  if (days == 0 || dayMask == 0x7f || dayMask == 0)    // don't care about week-day?
    return;
  int direction = (days > 0 ? 1 : -1);

  while (days != 0)
  {
    if (days > 0)
      m_Value += 1000000;   // one day
    else
      m_Value -= 1000000;

    int m = GetMonth();
    int d = GetDay();
    if (d < 1)
    {
      int y = GetYear();
      m--;
      if (m < 1)
        m = 12, y--;
      d = MonthDays[m-1];
      if (m == 2 && IsLeapYear(y))
        d++;
      Change(y, m, d);
    }
    else
    if (d > MonthDays[m-1])
    {
      int y = GetYear();
      m++;
      if (m > 12)
        m = 1, y++;
      d = 1;
      Change(y, m, d);
    }

    int dayBit = 1 << GetDayOfWeek();
    if ((dayBit & dayMask) != 0)
      days -= direction;
  } // while
}

static const char* const MonthStrings[] = { "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", NULL };

const char* ETime::Format (const char *format) const
{
  static THREADVAR char buf[100];
  if (NULL == format)
    format = "%Y-%m-%d %H:%M:%S";

  const char* pFormat = format;
  char* p = buf;

  while (*pFormat)
  {
    char literal = *pFormat++;
    if (literal == '%')
    {
      char formattingCode = *pFormat++;
      if (formattingCode == '\0')
        return NULL;
      else
      if (formattingCode != '%')
      {
        switch (formattingCode)
        {
        case 'b':     // abbreviated month name
          p += sprintf(p, "%s", MonthStrings[GetMonth()-1]);
          break;

        case 'd':
          p += sprintf(p, "%02d", GetDay());
          break;

        case 'H':
          p += sprintf(p, "%02d", GetHour());
          break;

        case 'm':
          p += sprintf(p, "%02d", GetMonth());
          break;

        case 'M':
          p += sprintf(p, "%02d", GetMinute());
          break;

        case 'S':
          p += sprintf(p, "%02d", GetSecond());
          break;

        case 'y':
          p += sprintf(p, "%02d", GetYear() % 100);
          break;

        case 'Y':
          p += sprintf(p, "%04d", GetYear());
          break;

        default:
          // this is a serious programming error!
          //ASSERT(false);
	  std::cout << "ERROR" << std::endl;
          return NULL;
        } // switch
        continue; // skip the literal handling below
      }
      // else fall down and expect '%' as litteral
    } // if
    *p++ = literal;
  } // while
  *p++ = '\0';
  
  return buf;
}


bool ETime::Unformat (const char *str, const char *format)
{
  int year = 0;
  int month = 0;
  int day = 0;
  int hour = 0;
  int minute = 0;
  int sec = 0;

  if (NULL == str)
    return false;

  if (NULL == format)
    format = "%Y-%m-%d %H:%M:%S";
  const char* pInTime = str;
  const char* pInFormat = format;

  while (*pInTime && *pInFormat)
  {
    char literalToExpect = *pInFormat++;
    if (literalToExpect == '%')
    {
      char buf[6] = { '\0' };
      char formattingCode = *pInFormat++;
      if (formattingCode == '\0')
        return false;
      else
      if (formattingCode != '%')
      {
        buf[0] = *pInTime++;
        if (isdigit(*pInTime))
          buf[1] = *pInTime++;
        switch (formattingCode)
        {
        case 'b':     // abbreviated month name
          {
            buf[1] = *pInTime++;
            buf[2] = *pInTime++;
            // _strlwr(buf);
            int i;
            for (i=0; i<12; i++)
              if (strcmp(buf, MonthStrings[i]) == 0)
                break;
            if (i >= 12)
              return false;
            month = i + 1;
          }
          break;

        case 'd':
          day = atoi(buf);
          break;

        case 'H':
          hour = atoi(buf);
          break;

        case 'm':
          month = atoi(buf);
          break;

        case 'M':
          minute = atoi(buf);
          break;

        case 'S':
          sec = atoi(buf);
          break;

        case 'y':
          year = atoi(buf);
          if (year < m_BreakYear_1900_2000)
            year += 2000;
          else
            year += 1900;
          break;

        case 'Y':
          buf[2] = *pInTime++;
          buf[3] = *pInTime++;
          year = atoi(buf);
          break;

        default:
          // this is a serious programming error!
          //ASSERT(false);
	  std::cout << "ERROR" << std::endl;
	  break;
        } // switch
        continue; // skip the literal handling below
      }
      // else fall down and expect '%' as litteral
    } // if

    if (*pInTime == literalToExpect)
      pInTime++;
    else
      return false;
  } // while

  Change(year, month, day, hour, minute, sec);
  return true;
}

void ETime::Change(int year, int month, int day, int hour, int minute, int sec)
{
  unsigned long YMD = (unsigned long)(m_Value / (__int64_t)1000000);

  if (-1 == year)
    year = YMD / 10000;

  if (-1 == month)
    month = (YMD / 100) % 100;
  
  if (-1 == day)
    day = YMD % 100;
  
  if (-1 == hour)
    hour = (int)(m_Value / 10000) % 100;
  
  if (-1 == minute)
    minute = (int)(m_Value / 100) % 100;
  
  if (-1 == sec)
    sec = (int)(m_Value % 100);

  m_Value = ((__int64_t)(year * 10000 + month * 100 + day) * (__int64_t)1000000) + (__int64_t)(hour * 10000 + minute * 100 + sec);
}
