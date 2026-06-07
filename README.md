# Microforce-Coer

**Microforce-Coer** is a next-generation, AI-native Semantic KVS (Key-Value Store) engine built on top of SQLite. 
It challenges the long-standing paradigm of traditional RDBMS (Relational Database Management Systems) by introducing a multi-dimensional "Mille-feuille" data structure optimized specifically for autonomous AI agents.

## The Paradigm Shift

For decades, RDBMS has dominated the industry because humans needed normalized tables to visually understand relationships and write SQL joins. However, in the AI era, human-readable normalization becomes a bottleneck.

AI execution engines process data faster and more accurately when it is provided as a unified, dimensional layer (Semantic KVS) without the overhead of complex SQL joins. Microforce-Coer is designed to bypass traditional MVC architectures and ORM mapping, allowing AI to directly ingest and manipulate data vectors.

## Features

- **Semantic KVS Layering**: Treats data, schemas, and UI constraints as independent, vectorized layers.
- **AI-Native Abstraction**: Designed for programmatic manipulation by MCP (Model Context Protocol) servers and AI agents.
- **High-Performance SQLite Core**: Leverages SQLite as the ultimate, portable KVS backend.
- **Maintenance-Free**: Completely autonomous operation without human database administration.

## How It Works: The Pandas Paradigm

The power of Microforce-Coer lies in treating the database not as a rigid structure of rows and columns, but as a storage layer for serialized, multi-dimensional data chunks (like Pandas DataFrames).

Instead of mapping a 2D array row-by-row into an ORM:
1. **Serialize**: Convert your Pandas DataFrame into a JSON layer (`df.to_json(orient='records')`).
2. **Store**: Swallow the entire 2D array as a single payload into the Semantic KVS (`layer_key = "hr:employees"`).
3. **Retrieve & Restore**: Read the payload back and instantly reconstruct the DataFrame (`pd.DataFrame(payload)`).

Zero SQL joins. Zero schema migrations. Pure vectorized speed.

👉 **[Read the Full Tutorial](docs/TUTORIAL.md)** for a hands-on guide with dummy data.
See `scripts/example_pandas_kvs.py` for a working demonstration.

## License

This project is licensed under the **Apache License 2.0**.
See the [LICENSE](LICENSE) file for details.
