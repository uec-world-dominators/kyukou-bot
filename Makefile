SOURCEDIR = './web/public'
MDS := $(shell find $(SOURCEDIR) -name '*.md')
HTMLS := $(MDS:%.md=%.html)
CSS = '/web/public/css/github.css'

%.html:%.md
	pandoc $< -t html5 -c $(CSS) --mathjax -o $@

default: $(HTMLS)

clean:
	rm $(HTMLS)