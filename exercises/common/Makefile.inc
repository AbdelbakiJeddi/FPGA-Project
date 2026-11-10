.RECIPEPREFIX = >
STD  ?= 08
WORK  = build
STOP ?= 1us

sim:
> mkdir -p $(WORK)
> ghdl -i --std=$(STD) --workdir=$(WORK) *.vhd
> ghdl -m --std=$(STD) --workdir=$(WORK) $(TOP)
> ghdl -r --std=$(STD) --workdir=$(WORK) $(TOP) --wave=$(WORK)/out.ghw --stop-time=$(STOP)

wave:
> gtkwave $(WORK)/out.ghw &

clean:
> rm -rf $(WORK) $(TOP)
