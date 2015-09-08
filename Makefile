


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
