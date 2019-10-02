```c
int main(){
    printf("%d",222)
}
```

```py
def main():
    print('hoge')
```

```makefile
ROOTDIR=#'/web/public'
SOURCEDIR = .$(ROOTDIR)
MDS := $(shell find $(SOURCEDIR) -name '*.md')
HTMLS := $(MDS:%.md=%.html)
CSS = $(ROOTDIR)/css/github.css

%.html:%.md
	pandoc $< -t html5 -c $(CSS) --mathjax -o $@ --highlight-style=tango

default: $(HTMLS)

clean:
	rm $(HTMLS)
```