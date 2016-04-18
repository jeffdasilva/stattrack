###############################################################################
#
# Jeff DaSilva
# Copyright 2016 All Rights Reserved
#
###############################################################################

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


#############################

.PHONY: all
all: check

PYTHON_UNITTEST_STAMPS := $(strip \
	$(patsubst %.py,stamps/%.unittest,\
	$(filter-out %/__init__.py,\
	$(filter-out $(PYTHON_MAIN),$(PYTHON_SRC))\
	)))

.PHONY: check
check: $(PYTHON_UNITTEST_STAMPS)

$(PYTHON_UNITTEST_STAMPS): stamps/%.unittest: %.py
	python -m unittest $(subst /,.,$*)
	@mkdir -p $(@D)
	@touch $@
#############################


#############################
.PHONY: tabs2space
tabs2space:
	@find . -type f -name '*.py' -exec sed -i 's/\t/    /g' {} \;

.PHONY: remove-trailing-whitespace
remove-trailing-whitespace:
	@find . -type f -name '*.py' -exec sed -i 's/[ \t]*$$//g' {} \;

.PHONY: lint
lint: remove-trailing-whitespace tabs2space
	$(MAKE) check
	$(MAKE) clean
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
CLEAN_FILES_RE += *.pyc *.class stamps test*.pickle *.orig *~
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


###############################################################################
#
# My git convenience targets
#

.PHONY: pull sync
pull sync: git-update

.PHONY: diff
diff: git-diff

.PHONY: push submit
push submit:
	$(MAKE) git-add-commit
	$(MAKE) git-push

.PHONY: git-update
git-update:
	git pull

.PHONY: git-add-commit
git-add-commit:
	git add -u
	git commit -a

.PHONY: git-config
git-config:
	git config --global core.editor emacs

git-set-remote:
	git remote set-url origin git@github.com:jeffdasilva/stattrack.git

.PHONY: git-push
git-push:
	git push origin master

.PHONY: git-diff git-status
git-diff git-status: git-%:
	git $*

.PHONY: git-log
git-log:
	git log | head -n12

# this one is dangerous, so be careful with it
.PHONY: git-revert git-reset
git-revert git-reset:
	git reset --hard

###############################################################################
