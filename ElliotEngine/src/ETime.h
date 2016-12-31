#ifndef ETime_h
#define ETime_h 1

#pragma once
#ifndef THREADVAR
#define THREADVAR
#endif

#define DAYSECONDS (3600*24)
#define WEEKSECONDS (3600*24*7)
#define MONTHSECONDS (3600*24*30)
#define YEARSECONDS (3600*24*365)
#define WEEKDAY_MON  0x02
#define WEEKDAY_TUE  0x04
#define WEEKDAY_WEN  0x08
#define WEEKDAY_THU  0x10
#define WEEKDAY_FRI  0x20
#define WEEKDAY_SAT  0x40
#define WEEKDAY_SUN  0x01
#define WEEKDAY_ONLY (WEEKDAY_MON | WEEKDAY_TUE | WEEKDAY_WEN | WEEKDAY_THU | WEEKDAY_FRI)


struct ETime
{
  ETime(__int64_t right = 0)  { m_Value = right;  }
  __int64_t operator = (__int64_t right) { m_Value = right; return m_Value; }

  operator __int64_t () const        { return m_Value;   }

  static bool IsLeapYear(int y);
  bool IsEOD() const;               // is End-Of-Day value? Returns true if time within day is 23:59:59
  int GetYMD() const;               // get integer in the form YYYYMMDD
  int GetYear() const;
  int GetMonth() const;
  int GetDay() const;
  int GetHour() const;
  int GetMinute() const;
  int GetSecond() const;
  int GetDayOfWeek() const;         // (0 - 6; Sunday = 0)
  double GetJulianDate() const;
  int GetSecondsWithinDay() const;

  // Returns true if the two objects represents a time on the same day; i.e. same year-month-day
  bool SameDay (const ETime& otherTime) const;

  // Note that the Diff function returns the diff in trading units (depending on the precision) 
  // if the dayMask is set to anything but 0x7f (implying don't care about weekends)!!!
  int Diff(const ETime& otherTime, int precision = DAYSECONDS, int dayMask = 0x7f) const;

  // moves n days forward (+) or backwards (-), and moves further in same direction depending on dayMask
  void MoveDays(int days, int dayMask = 0x7f);

  const char* Format (const char *format = 0) const;
  bool Unformat (const char *str, const char *format = 0);

  void Change (int year, int month, int day, int hour = -1, int minute = -1, int sec = -1);

  // in this implementation, the 64-bit value is divided such:
  // the date as an integer in the form YYYYMMDD is multiplied by one million (1000000)
  // and the time within the day is added as hhmmss
  __int64_t m_Value;

  static int m_TradingDayOpen;          // in seconds from start-of-day
  static int m_TradingDayClose;         // in seconds from start-of-day
  static int m_BreakYear_1900_2000;     // if a two-digit year value is above this, then it's the 1900's, otherwise the 2000's
};


inline int ETime::GetYMD() const
{
  return (unsigned long)(m_Value / 1000000);
}

inline int ETime::GetYear() const
{
  unsigned long YMD = (unsigned long)(m_Value / (__int64_t)1000000);
  return YMD / 10000;
}

inline int ETime::GetMonth() const
{
  unsigned long YMD = (unsigned long)(m_Value / (__int64_t)1000000);
  return (YMD / 100) % 100;
}

inline int ETime::GetDay() const
{
  unsigned long YMD = (unsigned long)(m_Value / (__int64_t)1000000);
  return YMD % 100;
}

inline int ETime::GetHour() const
{
  unsigned long withinDay = (unsigned long)(m_Value % (__int64_t)1000000);
  return (int)(withinDay / 10000) % 100;
}

inline int ETime::GetMinute() const
{
  unsigned long withinDay = (unsigned long)(m_Value % (__int64_t)1000000);
  return (int)(withinDay / 100) % 100;
}

inline int ETime::GetSecond() const
{
  unsigned long withinDay = (unsigned long)(m_Value % (__int64_t)1000000);
  return (int)(withinDay % 100);
}


#endif  // ETime_h
