DESTDIR =
UI_SOURCES = $(shell ls *.ui)
UI_PYFILES = $(patsubst %.ui, Ui_%.py, $(UI_SOURCES))
PYUIC = pyuic5

SUBDIRS = lang

.PHONY: all
all: $(UI_PYFILES)
	for d in $(SUBDIRS); do make -C $$d $@; done

.PHONY: clean
clean:
	rm -f $(UI_PYFILES)
	for d in $(SUBDIRS); do make -C $$d $@; done

.PHONY: install
install:
	for d in $(SUBDIRS); do make -C $$d $@; done

Ui_%.py: %.ui
	$(PYUIC) -o $@ $<
