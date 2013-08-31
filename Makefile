ALL := monitor.js

.PHONY: all

all: $(ALL)

%.js: %.coffee
	coffee --compile --output $(@D) $<

clean:
	rm -f $(ALL)
