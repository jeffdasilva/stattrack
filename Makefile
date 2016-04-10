###############################################################################
#
# Jeff DaSilva
# Copyright 2016 All Rights Reserved
#
###############################################################################

SHELL := /bin/bash
.SECONDEXPANSION:

PYTHON_SRC := $(wildcard *.py)

PYTHON_UNITTEST_STAMPS := $(patsubst %.py,stamps/%.unittest,$(PYTHON_SRC))

.PHONY: check
check: $(PYTHON_UNITTEST_STAMPS)

$(PYTHON_UNITTEST_STAMPS): stamps/%.unittest: %.py
	python -m unittest $*
	@mkdir -p $(@D)
	@touch $@

.PHONY: tabs2space
tabs2space:
	find . -type f -name '*.py' -exec sed -i.orig 's/\t/    /g' {} +

.PHONY: run
run:
	python stattrack.py

.PHONY:dev
dev:
	sublime-text Makefile $(PYTHON_SRC) &

.PHONY: clean
clean:
	rm -rf *.pyc *.class stamps test*.pickle *.orig *~



###############################################################################
#
# My git convenience targets
#

.PHONY: sync
sync: git-update

.PHONY: submit
submit:
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

.PHONY: git-push
git-push:
	git push origin master

.PHONY: git-diff git-status
git-diff git-status: git-%:
	git $*

###############################################################################
