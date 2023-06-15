source = infer.cc demo.cc process.cc sampledfunction.cc processforecaster.cc vbrssp.cc cellqueue.cc receiver.cc
objects = process.o sampledfunction.o processforecaster.o cellqueue.o receiver.o
executables = infer demo vbrssp

CXX = g++
CXXFLAGS = -I/opt/homebrew/Cellar/boost/1.81.0_1/include -g -O3 -std=c++14 -ffast-math -pedantic -Werror -Wall -Wextra -Weffc++ -pipe -Wno-unused-parameter -D_FILE_OFFSET_BITS=64 -D_XOPEN_SOURCE=500 -D_GNU_SOURCE
LIBS = -lm

all: $(executables)

infer: infer.o $(objects)
	$(CXX) $(CXXFLAGS) -o $@ $+ $(LIBS)

demo: demo.o $(objects)
	$(CXX) $(CXXFLAGS) -o $@ $+ $(LIBS)

vbrssp: vbrssp.o $(objects)
	$(CXX) $(CXXFLAGS) -o $@ $+ $(LIBS)

%.o: %.cc
	$(CXX) $(CXXFLAGS) -c -o $@ $<

-include depend

depend: $(source)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -MM $(source) > depend

.PHONY: clean
clean:
	-rm -f $(executables) depend *.o *.rpo
