ALL := scripts.js

.PHONY: all

all: $(ALL)

%.js: %.coffee
	coffee --compile --output $(@D) $<

scripts.js: json2.js monitor.js
	cat $^ | yui-compressor --type js --output $@

clean:
	rm -f $(ALL) $(patsubst %.coffee,%.js,$(wildcard *.coffee))
