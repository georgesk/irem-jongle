DESTDIR =

SUBDIRS = jongle

.PHONY: all
all:
	for d in $(SUBDIRS); do make -C $$d $@; done

.PHONY: clean
clean:
	rm -f *~
	for d in $(SUBDIRS); do make -C $$d $@; done

.PHONY: install
install:
	for d in $(SUBDIRS); do make -C $$d $@; done

.PHONY: html
html:
	make -C docs html
