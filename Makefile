OUTDIR := output
DATA := data
ARGS = $(INPUT) $(OUTDIR)

# EXAMPLE
.PHONY: example

example: INPUT := $(DATA)/example.txt
example: FLAGS := -w --teleportation-probability 0 $(ARGS)
example: clean all_representations

# MINIMAL EXAMPLE
.PHONY: minimal

minimal: INPUT := $(DATA)/minimal.txt
minimal: FLAGS := -w --teleportation-probability 0.15 $(ARGS)
minimal: clean weighted_representations

# EXAMPLE FOR PAPER
.PHONY: example_for_paper

example_for_paper: INPUT := $(DATA)/example-paper.txt
example_for_paper: FLAGS := -w -2 --teleportation-probability 0.15 $(ARGS)
example_for_paper: clean weighted_representations

# REFERENCES
.PHONY: references references_weighted

REFS := $(DATA)/references.txt
REFS_WEIGHTED := $(DATA)/references-weighted.txt
TEX_FILE := $(DATA)/networks-beyond-pairwise-interactions-references.tex

$(REFS):
	python -m references --omega log-citations $(TEX_FILE) $(REFS)

$(REFS_WEIGHTED):
	python -m references --omega log-citations --gamma-weighted $(TEX_FILE) $(REFS_WEIGHTED)

references: INPUT := $(REFS)
references:
	@$(MAKE) clean
	@$(MAKE) $(REFS)
	@$(MAKE) all_representations FLAGS="--largest-cc $(ARGS)"

references_weighted: INPUT := $(REFS_WEIGHTED)
references_weighted:
	@$(MAKE) clean
	@$(MAKE) $(REFS_WEIGHTED)
	@$(MAKE) weighted_representations FLAGS="--largest-cc $(ARGS)"


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
	weighted_representations \
	bipartite \
	bipartite_non_backtracking \
	unipartite_undirected \
	unipartite_undirected_self_links \
	unipartite_directed \
	unipartite_directed_self_links \
	multilayer \
	multilayer_self_links

weighted_representations: \
	bipartite \
	bipartite_non_backtracking \
	unipartite_directed \
	unipartite_directed_self_links \
	multilayer \
	multilayer_self_links \
	multilayer_similarity \
	multilayer_similarity_self_links

all_representations: \
	weighted_representations \
	unipartite_undirected \
	unipartite_undirected_self_links

bipartite:
	$(RUN) -b $(FLAGS)

bipartite_non_backtracking:
	$(RUN) -B $(FLAGS)

unipartite_undirected:
	$(RUN) -u $(FLAGS)

unipartite_undirected_self_links:
	$(RUN) -uk $(FLAGS)

unipartite_directed:
	$(RUN) -U $(FLAGS)

unipartite_directed_self_links:
	$(RUN) -Uk $(FLAGS)

multilayer:
	$(RUN) -m $(FLAGS)

multilayer_self_links:
	$(RUN) -mk $(FLAGS)

multilayer_similarity:
	$(RUN) -M $(FLAGS)

multilayer_similarity_self_links:
	$(RUN) -Mk $(FLAGS)

# CLEAN
.PHONY: clean

clean:
	$(RM) -r $(OUTDIR)/*.{clu,tree,ftree,net}
	$(RM) -r $(OUTDIR)/**/*.{clu,tree,ftree,net}
