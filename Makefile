OUTDIR := output
DATA := data
ALL_FLAGS = $(INPUT) $(OUTDIR)

# EXAMPLE
.PHONY: example

example: INPUT := $(DATA)/example.txt
example: FLAGS := -w --teleportation-probability 0 $(ALL_FLAGS)
example: clean all_representations

# REFERENCES
.PHONY: references create_references

REFS := $(DATA)/networks-beyond-pairwise-interactions.txt

references: INPUT := $(REFS)
references: FLAGS := $(ALL_FLAGS)
references: clean all_representations

TEX_FILE := $(DATA)/networks-beyond-pairwise-interactions-references.tex
WEIGHTED := --omega-weighted --gamma-weighted

create_references:
	python -m references $(WEIGHTED) $(TEX_FILE) $(REFS)

# REPRESENTATIONS
RUN := python -m hypergraph

.PHONY: \
	all_representations \
	bipartite \
	bipartite_non_backtracking \
	clique \
	clique_self_links \
	clique_directed \
	clique_directed_self_links \
	multilayer \
	multilayer_self_links

all_representations: \
	bipartite \
	bipartite_non_backtracking \
	clique \
	clique_self_links \
	clique_directed \
	clique_directed_self_links \
	multilayer \
	multilayer_self_links

bipartite:
	$(RUN) -b $(FLAGS)

bipartite_non_backtracking:
	$(RUN) -B $(FLAGS)

clique:
	$(RUN) -c $(FLAGS)

clique_self_links:
	$(RUN) -ck $(FLAGS)

clique_directed:
	$(RUN) -C $(FLAGS)

clique_directed_self_links:
	$(RUN) -Ck $(FLAGS)

multilayer:
	$(RUN) -m $(FLAGS)

multilayer_self_links:
	$(RUN) -mk $(FLAGS)

# CLEAN
.PHONY: clean

clean:
	$(RM) -r $(OUTDIR)/*.{ftree,net}
