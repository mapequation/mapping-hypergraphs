OUTDIR := output
DATA := data
ARGS = $(INPUT) $(OUTDIR)

# EXAMPLE
.PHONY: example

example: INPUT := $(DATA)/example.txt
example: FLAGS := -w --teleportation-probability 0 $(ARGS)
example: clean all_representations

# REFERENCES
.PHONY: references references_weighted

REFS := $(DATA)/references.txt
REFS_WEIGHTED := $(DATA)/references-weighted.txt
TEX_FILE := $(DATA)/networks-beyond-pairwise-interactions-references.tex

$(REFS):
	python -m references --omega-weighted $(TEX_FILE) $(REFS)

$(REFS_WEIGHTED):
	python -m references --omega-weighted --gamma-weighted $(TEX_FILE) $(REFS_WEIGHTED)

references: INPUT := $(REFS)
references:
	@$(MAKE) clean
	@$(MAKE) $(REFS)
	@$(MAKE) all_representations FLAGS="$(ARGS)"

references_weighted: INPUT := $(REFS_WEIGHTED)
references_weighted:
	@$(MAKE) clean
	@$(MAKE) $(REFS_WEIGHTED)
	@$(MAKE) weighted_representations FLAGS="$(ARGS)"


# SEEDS
SEEDS = 1 2 3 4 5 6 7 8 9 10
.PHONY: seeds $(SEEDS)

seeds:
	@$(MAKE) clean
	@$(MAKE) $(REFS)
	@$(MAKE) $(SEEDS)

$(SEEDS): INPUT := $(REFS)
$(SEEDS):
	@$(MAKE) all_representations FLAGS="--seed $(@) $(ARGS)"

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

weighted_representations: \
	bipartite \
	bipartite_non_backtracking \
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
