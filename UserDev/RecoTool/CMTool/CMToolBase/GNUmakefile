#
# This is an example GNUmakefile for CMToolBase package
#

# specific names for this package
DICT  = RecoTool_CMToolBaseDict
SHLIB = libRecoTool_CMToolBase.so
SOURCES = $(filter-out $(DICT).cxx, $(wildcard *.cxx))
FMWK_HEADERS = LinkDef.h $(DICT).h
HEADERS = $(filter-out $(FMWK_HEADERS), $(wildcard *.h))
OBJECTS = $(SOURCES:.cxx=.o)

# include options for this package
INCFLAGS  = -I.                       #Include itself
INCFLAGS += $(shell larlite-config --includes)
INCFLAGS += $(shell recotool-config --includes)
INCFLAGS += $(shell basictool-config --includes)
#INCFLAGS += -I$(LARLITE_USERDEVDIR)/RecoTool/ClusterRecoUtil/Alg

# platform-specific options
OSNAME          = $(shell uname -s)
HOST            = $(shell uname -n)
OSNAMEMODE      = $(OSNAME)

CINTFLAGS += -p

# linker flags
LDFLAGS += $(shell larlite-config --libs)
LDFLAGS += $(shell basictool-config --libs)
LDFLAGS += -L$(LARLITE_LIBDIR) -lRecoTool_ClusterRecoUtil
LDFLAGS += -L$(LARLITE_LIBDIR) -lRecoTool_ClusterRecoUtilAlg

include $(LARLITE_BASEDIR)/Makefile/Makefile.${OSNAME}

# call the common GNUmakefile
include $(LARLITE_BASEDIR)/Makefile/GNUmakefile.CORE



