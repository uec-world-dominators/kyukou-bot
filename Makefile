ROOTDIR=#'/web/public'
SOURCEDIR = ./web/public
MDS := $(shell find $(SOURCEDIR) -name '*.md')
HTMLS := $(MDS:%.md=%.html)
CSS = $(ROOTDIR)/css/github.css

%.html:%.md
	pandoc $< -t html5 -c $(CSS) --mathjax -o $@ --highlight-style=tango

default: $(HTMLS)

clean:
	rm $(HTMLS)