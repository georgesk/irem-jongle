UI_SOURCES = $(shell ls *.ui)
UI_PYFILES = $(patsubst %.ui, Ui_%.py, $(UI_SOURCES))
PYUIC = pyuic5

.PHONY: all
all: $(UI_PYFILES)

.PHONY: clean
clean:
	rm -f $(UI_PYFILES)

Ui_%.py: %.ui
	$(PYUIC) -o $@ $<
