# Fetch

Retrieve a URL and convert it to markdown an agent can read.

## Add it

```yaml
# workspace.yaml
mcp_servers:
- id: fetch
  transport: stdio
  command:
  - uvx
  - mcp-server-fetch
  permission: readonly
  effects:
    fetch: read
```

```yaml
# a topology or archetype
skills:
  - pack:fetch    # every read skill below
```

Needs swarmkit-runtime **>=1.199.0**. Upstream: `pypi mcp-server-fetch`.

## Skills

### `fetch-url`

| | |
| --- | --- |
| tool | `fetch` |
| category | capability |
| effects | **read** |

**What it does.** Fetches a URL and returns it as markdown.

**Why you would want it.** Raw HTML wastes most of a context window on markup. Converting first means the agent reads the page rather than the page's scaffolding.

**When to grant it.** Give it to research and documentation agents. It reaches the public internet — think about that before granting it to an agent handling private data.
