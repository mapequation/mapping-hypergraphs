# Create network representation from hypergraph

Fast Rust implementation of the Mapping hypergraphs Python code.

This is useful for creating network representations of large hypergraphs,
for example the paleo marine faunas hypergraph.

Note that as the each layer in the multiayer representation are fully connected, the resulting
files are quite large (~GB).

## Usage

Build the release build (much faster than debug)

```bash
cargo build --release
```

Usage
```
cargo run -- representation hypergraph outfile
```
Where `representation` can be any of `-[b|B|u|U|m|M|hs|HS]` and the hypergraph
is in the same format as in the main repository.

See [config.rs](src/config.rs) for more information.

## Author
Anton Eriksson