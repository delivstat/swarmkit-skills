# DuckDB

Run SQL over local files — CSV, Parquet, JSON — with no database to operate.

The one analytical database with no dependency to stand up: DuckDB reads a CSV or Parquet file
directly, so `SELECT … FROM 'data/*.parquet'` works against a directory with no import step.

The command above is an **in-memory scratchpad** — nothing persists, which is what makes it safe to
verify in CI and a good default for analysis over files. Point it at a file instead to keep results:

```yaml
command: [uvx, mcp-server-motherduck, --db-path, "${SWARMKIT_DUCKDB_PATH}"]
```

A file path without `--read-write` opens read-only, and *that* configuration deserves
`permission: readonly` — the one above does not, because `execute_query` takes arbitrary SQL and
`CREATE TABLE` is arbitrary SQL. The effects map says so rather than trusting the tool's name.

## Add it

```yaml
# workspace.yaml
mcp_servers:
- id: duckdb
  transport: stdio
  command:
  - uvx
  - mcp-server-motherduck
  - --db-path
  - ':memory:'
  - --read-write
  permission: cautious
  effects:
    list_databases: read
    list_tables: read
    list_columns: read
    execute_query: write
```

```yaml
# a topology or archetype
skills:
  - pack:duckdb    # every read skill below
```

Writes are never in that. Name them:

```yaml
skills:
  - pack:duckdb
  - duckdb-query
```

Needs swarmkit-runtime **>=1.199.0**. Upstream: `pypi mcp-server-motherduck`.

## Skills

### `duckdb-list-tables`

| | |
| --- | --- |
| tool | `list_tables` |
| category | capability |
| effects | **read** |

**What it does.** Lists the tables and views in the database, with their comments.

**Why you would want it.** An agent writing SQL against a schema it has not seen invents column names. This is the call that stops that.

**When to grant it.** Grant it alongside any query skill — always, not optionally.

### `duckdb-list-columns`

| | |
| --- | --- |
| tool | `list_columns` |
| category | capability |
| effects | **read** |

**What it does.** Lists a table's columns with types and comments.

**Why you would want it.** Types decide whether a comparison is a comparison or a string mismatch, and the comments are often the only documentation the data has.

**When to grant it.** Same rule as list-tables: schema before query.

### `duckdb-query`

| | |
| --- | --- |
| tool | `execute_query` |
| category | capability |
| effects | **write** |

**What it does.** Executes a SQL query. In the in-memory configuration above, against files on disk.

**Why you would want it.** SQL over a directory of Parquet files, with no ingestion and no server, is the cheapest analytical capability available to a swarm.

**When to grant it.** Effect is **write**, and not as a formality: the tool takes arbitrary SQL, so `INSERT` and `CREATE` reach it too. It is refused under `permission: readonly` and never carried by `pack:duckdb`. Grant it by name to the agent that needs it.
