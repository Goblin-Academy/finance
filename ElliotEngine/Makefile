IDIR =src
IDIR2 =ChartDirector/include
CC=gcc
#CFLAGS=-I$( IDIR) -stdlib=libstdc++ -lstdc++ -g -Wall `root-config --libs --cflags`
CFLAGS=-I$(IDIR) -I$(IDIR2) -lstdc++ -g -Wall -L./ChartDirector/lib `root-config --libs --cflags`

ODIR=obj
LIBS=-lm

_DEPS = ewave_lib.h ETime.h StdAfx.h Resource.h ElliotRun.h #ElliotEngineDoc.h DummyView.h #ElliotEngineView.h  ChildFrm.h MainFrm.h
DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

_OBJ = ewave_lib.o ETime.o StdAfx.o ElliotRun.o #ElliotEngineDoc.o DummyView.o #ElliotEngineView.o ChildFrm.o  MainFrm.o 
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))

$(ODIR)/%.o: $(IDIR)/%.cpp $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)
ElliotRun: $(OBJ)
	gcc -o $@ $^ $(CFLAGS) $(LIBS)

.PHONY: clean

clean:
	rm -f $(ODIR)/*.o *~ core $(IDIR)/*~ 
