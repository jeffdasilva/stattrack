###############################################################################
#
# Jeff DaSilva
# Copyright 2016 All Rights Reserved
#
###############################################################################

#############################
#
# prerequisites:
#  % sudo apt-get install python-bs4
#  % sudo easy_install jsonpickle
#
# unittest by doing:
#  % make
#
# Run with:
#  % make run
#############################


#############################
SHELL := /bin/bash
.SECONDEXPANSION:

SPACE := $(empty) $(empty)

.PHONY: default
default: check
#############################


#############################
PYTHON_PACKAGES = $(foreach subdir,* */* */*/* */*/*/*,$(patsubst %/__init__.py,%,$(wildcard $(subdir)/__init__.py)))
PYTHON_SRC := $(wildcard *.py) $(foreach pkg,$(PYTHON_PACKAGES),$(wildcard $(pkg)/*.py))
PYTHON_MAIN := stattrack.py
#############################


GIT_PUSH_DEPS = increment-minor-version

#############################
# boilerplate build infra
include bcommon/inc.mk
#############################


#############################

.PHONY: all
all: check

PYTHON_UNITTEST_STAMPS := $(strip \
	$(patsubst %.py,stamps/%.unittest,\
	$(filter-out %__init__.py,\
	$(PYTHON_SRC)\
	)))

.PHONY: check
check: $(PYTHON_UNITTEST_STAMPS)

$(PYTHON_UNITTEST_STAMPS): stamps/%.unittest: %.py
	python -m unittest $(subst /,.,$*)
	@mkdir -p $(@D)
	@touch $@


PYTHON_PYLINT_STAMPS := $(strip \
	$(patsubst %.py,stamps/%.pylint,\
	$(filter-out %__init__.py,\
	$(PYTHON_SRC)\
	)))

.PHONY: pylint
pylint: $(PYTHON_PYLINT_STAMPS)

$(PYTHON_PYLINT_STAMPS): stamps/%.pylint: %.py
	@mkdir -p $(@D)
	-pylint $< > $@
	cat $@
	
	
.PHONY: uml
uml:
	pyreverse -ASmy -k -o png $(PYTHON_SRC) -p stattrack


#############################


#############################
.PHONY: tabs2space
tabs2space:
	@find . -type f -name '*.py' -exec sed -i 's/\t/    /g' {} \;

.PHONY: remove-trailing-whitespace
remove-trailing-whitespace:
	@find . -type f -name '*.py' -exec sed -i 's/[ \t]*$$//g' {} \;

.PHONY: remove-windows-line-endings
remove-windows-line-endings:
ifeq ($(shell which dos2unix 2>/dev/null),)
	$(warning WARNING: dos2unix not installed)
	@sleep 2
else 
	@find . -type f \( -name '*.py' -o -name 'Makefile' -o -name '*.mk' -o -name '*.md' -o -name 'LICENSE' \) \
		-exec dos2unix {} \;
endif

.PHONY: lint
lint: increment-build-number remove-trailing-whitespace remove-windows-line-endings tabs2space
	$(MAKE) check
	$(MAKE) clean
#############################


#############################
CURRENT_BUILD_NUMBER = $(shell grep "BuildNumber = [0-9]*$$" $(PYTHON_MAIN) | head -n1 | sed -e 's,.*=[ \t]*,,g')
NEXT_BUILD_NUMBER = $(shell echo $$[$(CURRENT_BUILD_NUMBER)+1])

.PHONY: increment-build-number
increment-build-number:
ifeq ($(shell whoami),jdasilva)
	@echo "Incrementing build number to: $(NEXT_BUILD_NUMBER)"
	@sed -i -e 's,\(BuildNumber = \)\([0-9]*\)$$,\1$(NEXT_BUILD_NUMBER),g' $(PYTHON_MAIN)
endif

CURRENT_MINOR_VERSION_NUMBER = $(shell grep "MinorVersion = [0-9]*$$" $(PYTHON_MAIN) | head -n1 | sed -e 's,.*=[ \t]*,,g')
NEXT_MINOR_VERSION_NUMBER = $(shell echo $$[$(CURRENT_MINOR_VERSION_NUMBER)+1])

.PHONY: increment-minor-version
increment-minor-version:
ifeq ($(shell whoami),jdasilva)
	@echo "Incrementing minor version number to: $(NEXT_MINOR_VERSION_NUMBER)"
	@sed -i -e 's,\(MinorVersion = \)\([0-9]*\)$$,\1$(NEXT_MINOR_VERSION_NUMBER),g' $(PYTHON_MAIN)
endif


#############################



#############################
.PHONY: run
run:
	python $(PYTHON_MAIN)
#############################


#############################
.PHONY: dev
dev:
	sublime-text Makefile $(PYTHON_SRC) &
#############################

#############################
CLEAN_FILES_RE += *.pyc *.class stamps test*.pickle *.orig *~ *.png
CLEAN_FILES += $(sort $(wildcard $(strip \
	$(foreach dir,. $(PYTHON_PACKAGES),\
	$(foreach clean_re,$(CLEAN_FILES_RE), \
		$(dir)/$(clean_re) \
)))))

.PHONY: clean
clean:
	$(if $(CLEAN_FILES),rm -rf $(CLEAN_FILES))

TARBALL_TIMESTAMP := $(strip $(subst $(SPACE),,$(shell date +%m%d%Y_%k%M%S)))
TARBALL_FILE := tgz/$(notdir $(abspath .))_$(TARBALL_TIMESTAMP).tar.gz

.PHONY: archive tarball tgz
archive tarball tgz: $(TARBALL_FILE)

$(TARBALL_FILE): clean
	@mkdir -p $(@D)
	@echo "Generating $@..."
	tar -czf $@ $(filter-out tgz,$(wildcard *))
#############################


