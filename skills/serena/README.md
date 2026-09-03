# Serena

Symbol-level code operations from a language server — find definitions, references and implementations.

Grep finds a string; a language server finds the symbol. For a swarm reasoning about code that
difference is most of the accuracy — `find_referencing_symbols` on a method returns its callers, not
every file containing that word.

Installed from git rather than PyPI because that is what upstream publishes. First start is slow: it
indexes the project and downloads a language server for it.

`--project` is required, so the workspace must supply `SWARMKIT_SERENA_PROJECT`. Serena also has
write tools, including `rename_symbol` across a whole codebase; the two included here are named
individually and cannot arrive through a bundle grant.

## Add it

```yaml
# workspace.yaml
mcp_servers:
- id: serena
  transport: stdio
  command:
  - uvx
  - --from
  - git+https://github.com/oraios/serena
  - serena
  - start-mcp-server
  - --context
  - ide-assistant
  - --project
  - ${SWARMKIT_SERENA_PROJECT}
  permission: cautious
  effects:
    get_symbols_overview: read
    find_symbol: read
    find_referencing_symbols: read
    find_implementations: read
    find_declaration: read
    get_diagnostics_for_file: read
    replace_symbol_body: write
    rename_symbol: write
```

```yaml
# a topology or archetype
skills:
  - pack:serena    # every read skill below
```

Writes are never in that. Name them:

```yaml
skills:
  - pack:serena
  - serena-replace-symbol-body
```

Needs swarmkit-runtime **>=1.199.0**. Upstream: `git github.com/oraios/serena`.

## Skills

### `serena-symbols-overview`

| | |
| --- | --- |
| tool | `get_symbols_overview` |
| category | capability |
| effects | **read** |

**What it does.** Lists the symbols defined in a file — classes, methods, functions.

**Why you would want it.** Lets an agent understand a file's shape without reading it, which is the difference between a hundred tokens and ten thousand.

**When to grant it.** The right first call on any unfamiliar file. Grant it to every code-reading agent.

### `serena-find-symbol`

| | |
| --- | --- |
| tool | `find_symbol` |
| category | capability |
| effects | **read** |

**What it does.** Finds a symbol by name path and returns its location and definition.

**Why you would want it.** Goes to the definition instead of guessing which of nine same-named functions is the one. Grep cannot tell them apart.

**When to grant it.** The entry point for any code question. Grant it with symbols-overview.

### `serena-find-references`

| | |
| --- | --- |
| tool | `find_referencing_symbols` |
| category | capability |
| effects | **read** |

**What it does.** Finds everything that references a symbol.

**Why you would want it.** This is the impact-analysis call. *What breaks if I change this* is not answerable by search, because a caller need not mention the name in a form grep can match.

**When to grant it.** Grant it to review and refactoring agents. It is what makes a change-impact claim more than an opinion.

### `serena-find-implementations`

| | |
| --- | --- |
| tool | `find_implementations` |
| category | capability |
| effects | **read** |

**What it does.** Finds the implementations of an interface or abstract method.

**Why you would want it.** The one navigation that is genuinely hard without a language server: an interface's name appears nowhere in the class that implements it in most languages.

**When to grant it.** Useful anywhere the codebase leans on interfaces or protocols.

### `serena-diagnostics`

| | |
| --- | --- |
| tool | `get_diagnostics_for_file` |
| category | capability |
| effects | **read** |

**What it does.** Returns the language server's diagnostics for a file — errors and warnings.

**Why you would want it.** The compiler's opinion, which beats the model's. An agent that checks this before proposing a change stops proposing code that does not type-check.

**When to grant it.** Grant it to any agent that writes code, as its self-check.

### `serena-replace-symbol-body`

| | |
| --- | --- |
| tool | `replace_symbol_body` |
| category | capability |
| effects | **write** |

**What it does.** Replaces the body of a symbol, leaving its signature alone.

**Why you would want it.** A structural edit rather than a line-range one, so it does not corrupt a file when the line numbers have moved since the agent last looked.

**When to grant it.** Effect is **write**. Named individually, refused under `readonly`, never carried by `pack:serena`.
