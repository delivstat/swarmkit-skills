# Memory

A knowledge graph the agent can write to and read back.

## Add it

```yaml
# workspace.yaml
mcp_servers:
- id: memory
  transport: stdio
  command:
  - npx
  - -y
  - '@modelcontextprotocol/server-memory'
  permission: cautious
  effects:
    read_graph: read
    search_nodes: read
    open_nodes: read
    create_entities: write
    create_relations: write
    add_observations: write
    delete_entities: write
    delete_relations: write
```

```yaml
# a topology or archetype
skills:
  - pack:memory    # every read skill below
```

Needs swarmkit-runtime **>=1.199.0**. Upstream: `npm @modelcontextprotocol/server-memory`.

## Skills

### `memory-search`

| | |
| --- | --- |
| tool | `search_nodes` |
| category | capability |
| effects | **read** |

**What it does.** Searches the knowledge graph.

**Why you would want it.** Recall without re-reading. An agent that can look up what it already established stops rediscovering it every run.

**When to grant it.** Pair with memory-write in long-running or multi-session work.

### `memory-write`

| | |
| --- | --- |
| tool | `create_entities` |
| category | capability |
| effects | **write** |

**What it does.** Adds entities to the knowledge graph.

**Why you would want it.** Declared effects: write. What an agent stores it can later act on, so what goes in matters more than it first appears.

**When to grant it.** Consider SwarmKit's own governed-memory skill instead where writes need a reconcile decision.
