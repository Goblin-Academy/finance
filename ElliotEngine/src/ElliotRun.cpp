// C++
#include <vector>
#include <iostream>
#include <fstream>
#include <set>
#include <map>

#include "ElliotRun.h"

using namespace std;

CLParser::CLParser(int argc_, char * argv_[],bool switches_on_)
{
  argc=argc_;
  argv.resize(argc);
  copy(argv_,argv_+argc,argv.begin());
  switches_on=switches_on_;

  //map the switches to the actual
  //arguments if necessary
  if (switches_on)
    {
      vector<string>::iterator it1,it2;
      it1=argv.begin();
      it2=it1+1;

      while (true)
        {
	  if (it1==argv.end()) break;
	  if (it2==argv.end()) break;

	  if ((*it1)[0]=='-')
	    switch_map[*it1]=*(it2);

	  it1++;
	  it2++;
        }
    }
}

string CLParser::get_arg(int i)
{
  if (i>=0&&i<argc)
    return argv[i];

  return "";
}

string CLParser::get_arg(string s)
{
  if (!switches_on) return "";

  if (switch_map.find(s)!=switch_map.end())
    return switch_map[s];

  return "";
}

int main(int argc, char * argv[]){

  ElliotRun elliot;
  return elliot.main(argc,argv);
}

ElliotRun::ElliotRun(){}

ElliotRun::~ElliotRun(){}


int ElliotRun::main(int argc, char * argv[]){
  CLParser cmd_line(argc,argv,true);

  cout << "printing the whole arg list...\n" << endl;
  for (int i=0; i<argc; i++)
    cout << cmd_line.get_arg(i) << endl;

  cout << "\nprinting the switch values...\n" << endl;

string temp;

  temp=cmd_line.get_arg("-i");
  if (temp!=""){
    cout << "Input: " << temp << endl;
  }else{ cout << "Need to give an input! -i" << std::endl; return 0; }
  const char * dir_name = temp.c_str();
  string dir_name_str = temp;
  std::cout << "reading text file: " << dir_name << std::endl;
  temp=cmd_line.get_arg("-o");
  if (temp!=""){ cout << "Output Name: " << temp << endl;
  }else{ cout << "Need to give an output! -o" << std::endl; return 0; }
  //const char *end_file_name = temp.c_str();
  string end_file_name = temp.c_str();

  
  return 1;
}
