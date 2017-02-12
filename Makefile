
PROD_COLORS := ir_black molokai wombat xoria256 zenburn
PROD_COLORS_IN := $(patsubst %,./schemes/%.vim,$(PROD_COLORS))
PROD_COLORS_OUT := $(patsubst %,./output/%.jcf,$(PROD_COLORS))

ALL_COLORS_IN := $(wildcard ./schemes/*.vim)
ALL_COLORS_OUT := $(patsubst ./schemes/%.vim,./output/%.jcf,$(ALL_COLORS_IN))


# Considering
#   darkspectrum, freya, inkpot, lucius, moria-light
# Fringe
#   candycode, moria-dark, peaksea-dark, slate, synic, tango2
# Deficient
#   darkblue2, desert, dusk, railscasts, tango
#
# Consider in the future:
#   tender, papercolor-light, dracula, base16, twilight, seoul256, desertink

#dbg:
#	sh -c "echo $(PROD_COLORS_OUT)"
#	sh -c "echo $(PROD_COLORS_IN)"
#	sh -c "echo $(ALL_COLORS_OUT)"
#	sh -c "echo $(ALL_COLORS_IN)"

prod: $(PROD_COLORS_OUT)
all: $(ALL_COLORS_OUT)

venv: requirements.txt
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt

clean:
	rm -rf ./output/*.jcf

install: 
	rm ~/src/joe/inst/share/joe/colors/*
	cp ./output/*.jcf ~/src/joe/inst/share/joe/colors
	cp ./custom/*.jcf ~/src/joe/inst/share/joe/colors

output/%.jcf : schemes/%.vim *.py venv overrides.json
	venv/bin/python3 convertvim.py $< > $@
