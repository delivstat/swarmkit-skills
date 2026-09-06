# SwarmKit skills

Pre-wired MCP servers and the skills that use them, for [SwarmKit](https://github.com/delivstat/swarmkit).

**The point is not the list — it is that each entry has been started and asked.** A curated list
nobody re-checks becomes an awesome-list, and those rot in months: a server renames a tool, changes
an argument, or disappears, and the entry keeps claiming it works. A nightly job starts every server
here and asks whether the tool each skill names still exists, so *verified* carries a date rather
than a promise.

**13 bundles · 39 skills.**

## How an entry is checked

Four questions, because *the tool exists* is the weakest of them and the easiest to mistake for
the others.

| | question | when |
| --- | --- | --- |
| **liveness** | does the tool this skill names still exist? | nightly |
| **schema** | is every skill a valid SwarmKit Skill, and does the example workspace load? | per push |
| **governance** | under `permission: readonly`, does the runtime's own gate allow the reads and deny the writes? | per push |
| **invocation** | called for real, does the tool answer — and does the server's own `readOnlyHint` agree with the effects we declared? | per push |

The last one matters most. Everything else compares a bundle against itself, so an effects map
that simply lies — `write_file: read` — passes them all; the gate's job is to believe the
declaration. The server's own hint is the one independent opinion available, and it is checked
against every declared effect on every server that publishes one.

[`examples/repo-report/`](examples/repo-report/) is a runnable workspace assembled only from
bundle blocks, pasted unchanged. It is the showcase and the fixture: CI loads it with the real
runtime, so a block SwarmKit cannot parse fails here rather than in your terminal.

## What you get for the paste

The hard part of adopting an MCP server is never the server. It is the `mcp_servers` block with the
right command and env, a `permission` tier, an `effects` map so `readonly` means something, an
`iam.required_scopes` that is neither too broad nor missing, and the argument shape the tool actually
wants. Every entry here has that already written down and checked.

## Index

| | bundle | skills | needs | verified |
| --- | --- | --- | --- | --- |
| ✅ | [Chrome DevTools](skills/chrome-devtools/) | 5 | `npm chrome-devtools-mcp` | 2026-09-06 |
| ✅ | [Context7](skills/context7/) | 2 | `npm @upstash/context7-mcp` | 2026-09-06 |
| ✅ | [DuckDB](skills/duckdb/) | 3 | `pypi mcp-server-motherduck` | 2026-09-06 |
| ✅ | [Excel](skills/excel/) | 6 | `pypi excel-mcp-server` | 2026-09-06 |
| ✅ | [Fetch](skills/fetch/) | 1 | `pypi mcp-server-fetch` | 2026-09-06 |
| ✅ | [Filesystem](skills/filesystem/) | 4 | `npm @modelcontextprotocol/server-filesystem` | 2026-09-06 |
| ✅ | [Git](skills/git/) | 3 | `pypi mcp-server-git` | 2026-09-06 |
| ✅ | [MarkItDown](skills/markitdown/) | 1 | `pypi markitdown-mcp` | 2026-09-06 |
| ✅ | [Memory](skills/memory/) | 2 | `npm @modelcontextprotocol/server-memory` | 2026-09-06 |
| ✅ | [Playwright](skills/playwright/) | 3 | `npm @playwright/mcp` | 2026-09-06 |
| ✅ | [Sequential Thinking](skills/sequential-thinking/) | 1 | `npm @modelcontextprotocol/server-sequential-thinking` | 2026-09-06 |
| ✅ | [Serena](skills/serena/) | 6 | `git github.com/oraios/serena` | 2026-09-06 |
| ✅ | [Time](skills/time/) | 2 | `pypi mcp-server-time` | 2026-09-06 |

| mark | meaning |
| --- | --- |
| ✅ | the server started and every tool below was present, on the date shown |
| 🔑 | needs a credential public CI does not have — nobody has checked it for you |
| ❌ | a tool it names is gone; see the linked issue |
| ⬜ | not yet checked |

`🔑` is not a lesser badge for a worse entry — it is an honest one. Roughly three in five of the
most-wanted MCP servers need somebody's account, and a green tick that meant *we did not look*
would be worth less than no tick at all.

## Using one

Copy the `mcp_servers` entry from a bundle's page into your `workspace.yaml`, copy its skill files
into `skills/`, and grant them:

```yaml
skills:
  - pack:git          # every READ skill in the bundle, now and later
  - fs-write-file     # a write, named — bulk grants never carry one
```

A `pack:` grant carries reads only. Adding a read skill to a bundle reaches everyone holding it;
adding a write reaches nobody, so a bundle can never silently widen an agent that already has it.

## The bundles

### ✅ [Chrome DevTools](skills/chrome-devtools/)

Diagnose a page: performance traces, console errors, network requests and a Lighthouse audit.

Needs swarmkit-runtime `>=1.199.0` · upstream `npm chrome-devtools-mcp`

| skill | tool | effects |
| --- | --- | --- |
| [`cdt-analyze-insight`](skills/chrome-devtools/README.md) | `performance_analyze_insight` | read |
| [`cdt-console-messages`](skills/chrome-devtools/README.md) | `list_console_messages` | read |
| [`cdt-lighthouse-audit`](skills/chrome-devtools/README.md) | `lighthouse_audit` | read |
| [`cdt-network-requests`](skills/chrome-devtools/README.md) | `list_network_requests` | read |
| [`cdt-performance-trace`](skills/chrome-devtools/README.md) | `performance_start_trace` | write |

### ✅ [Context7](skills/context7/)

Up-to-date documentation for a library, fetched on demand.

Needs swarmkit-runtime `>=1.199.0` · upstream `npm @upstash/context7-mcp`

| skill | tool | effects |
| --- | --- | --- |
| [`library-docs`](skills/context7/README.md) | `query-docs` | read |
| [`resolve-library-id`](skills/context7/README.md) | `resolve-library-id` | read |

### ✅ [DuckDB](skills/duckdb/)

Run SQL over local files — CSV, Parquet, JSON — with no database to operate.

Needs swarmkit-runtime `>=1.199.0` · upstream `pypi mcp-server-motherduck`

| skill | tool | effects |
| --- | --- | --- |
| [`duckdb-list-columns`](skills/duckdb/README.md) | `list_columns` | read |
| [`duckdb-list-tables`](skills/duckdb/README.md) | `list_tables` | read |
| [`duckdb-query`](skills/duckdb/README.md) | `execute_query` | write |

### ✅ [Excel](skills/excel/)

Read and write .xlsx workbooks — data, formulas, formatting — with no Excel installed.

Needs swarmkit-runtime `>=1.199.0` · upstream `pypi excel-mcp-server`

| skill | tool | effects |
| --- | --- | --- |
| [`excel-apply-formula`](skills/excel/README.md) | `apply_formula` | write |
| [`excel-read-data`](skills/excel/README.md) | `read_data_from_excel` | read |
| [`excel-validate-formula`](skills/excel/README.md) | `validate_formula_syntax` | read |
| [`excel-validate-range`](skills/excel/README.md) | `validate_excel_range` | read |
| [`excel-workbook-metadata`](skills/excel/README.md) | `get_workbook_metadata` | read |
| [`excel-write-data`](skills/excel/README.md) | `write_data_to_excel` | write |

### ✅ [Fetch](skills/fetch/)

Retrieve a URL and convert it to markdown an agent can read.

Needs swarmkit-runtime `>=1.199.0` · upstream `pypi mcp-server-fetch`

| skill | tool | effects |
| --- | --- | --- |
| [`fetch-url`](skills/fetch/README.md) | `fetch` | read |

### ✅ [Filesystem](skills/filesystem/)

Read, write and search files under a directory you nominate.

Needs swarmkit-runtime `>=1.199.0` · upstream `npm @modelcontextprotocol/server-filesystem`

| skill | tool | effects |
| --- | --- | --- |
| [`fs-list-directory`](skills/filesystem/README.md) | `list_directory` | read |
| [`fs-read-file`](skills/filesystem/README.md) | `read_file` | read |
| [`fs-search-files`](skills/filesystem/README.md) | `search_files` | read |
| [`fs-write-file`](skills/filesystem/README.md) | `write_file` | write |

### ✅ [Git](skills/git/)

Read history, diffs and blame from a local repository.

Needs swarmkit-runtime `>=1.199.0` · upstream `pypi mcp-server-git`

| skill | tool | effects |
| --- | --- | --- |
| [`git-diff`](skills/git/README.md) | `git_diff` | read |
| [`git-log`](skills/git/README.md) | `git_log` | read |
| [`git-status`](skills/git/README.md) | `git_status` | read |

### ✅ [MarkItDown](skills/markitdown/)

Convert a PDF, Office document, image or web page to markdown.

Needs swarmkit-runtime `>=1.199.0` · upstream `pypi markitdown-mcp`

| skill | tool | effects |
| --- | --- | --- |
| [`convert-to-markdown`](skills/markitdown/README.md) | `convert_to_markdown` | read |

### ✅ [Memory](skills/memory/)

A knowledge graph the agent can write to and read back.

Needs swarmkit-runtime `>=1.199.0` · upstream `npm @modelcontextprotocol/server-memory`

| skill | tool | effects |
| --- | --- | --- |
| [`memory-search`](skills/memory/README.md) | `search_nodes` | read |
| [`memory-write`](skills/memory/README.md) | `create_entities` | write |

### ✅ [Playwright](skills/playwright/)

Drive a real browser: navigate, click, fill, and read the page.

Needs swarmkit-runtime `>=1.199.0` · upstream `npm @playwright/mcp`

| skill | tool | effects |
| --- | --- | --- |
| [`browser-click`](skills/playwright/README.md) | `browser_click` | write |
| [`browser-navigate`](skills/playwright/README.md) | `browser_navigate` | write |
| [`browser-snapshot`](skills/playwright/README.md) | `browser_snapshot` | read |

### ✅ [Sequential Thinking](skills/sequential-thinking/)

A structured scratchpad for multi-step reasoning.

Needs swarmkit-runtime `>=1.199.0` · upstream `npm @modelcontextprotocol/server-sequential-thinking`

| skill | tool | effects |
| --- | --- | --- |
| [`sequential-thinking`](skills/sequential-thinking/README.md) | `sequentialthinking` | read |

### ✅ [Serena](skills/serena/)

Symbol-level code operations from a language server — find definitions, references and implementations.

Needs swarmkit-runtime `>=1.199.0` · upstream `git github.com/oraios/serena`

| skill | tool | effects |
| --- | --- | --- |
| [`serena-diagnostics`](skills/serena/README.md) | `get_diagnostics_for_file` | read |
| [`serena-find-implementations`](skills/serena/README.md) | `find_implementations` | read |
| [`serena-find-references`](skills/serena/README.md) | `find_referencing_symbols` | read |
| [`serena-find-symbol`](skills/serena/README.md) | `find_symbol` | read |
| [`serena-replace-symbol-body`](skills/serena/README.md) | `replace_symbol_body` | write |
| [`serena-symbols-overview`](skills/serena/README.md) | `get_symbols_overview` | read |

### ✅ [Time](skills/time/)

Current time and timezone conversion.

Needs swarmkit-runtime `>=1.199.0` · upstream `pypi mcp-server-time`

| skill | tool | effects |
| --- | --- | --- |
| [`convert-time`](skills/time/README.md) | `convert_time` | read |
| [`current-time`](skills/time/README.md) | `get_current_time` | read |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The short version: a bundle must declare `effects` for every
tool, carry a `requires_runtime` floor, and pass the liveness check — or say honestly why it cannot.

<sub>This file is generated by `scripts/build_readme.py`. Edit the bundles, not this.</sub>
