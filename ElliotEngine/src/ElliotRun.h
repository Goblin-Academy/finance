// ElliotRun.h : main header file for the ELLIOTENGINE application
//

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#include "Resource.h"       // main symbols

// C++
#include <fstream>
#include <dirent.h>
#include <errno.h>

class CLParser
{
public:

  CLParser(int argc_, char * argv_[],bool switches_on_=false);
  ~CLParser(){}

  std::string get_arg(int i);
  std::string get_arg(std::string s);

private:

  int argc;
  std::vector<std::string> argv;

  bool switches_on;
  std::map<std::string,std::string> switch_map;
};

int main(int nvar, char *testv[]);

class ElliotRun
{
 public:
  ElliotRun();
  virtual ~ElliotRun();

  int main(int nvar, char *testv[]);
};




