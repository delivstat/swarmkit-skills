# Sequential Thinking

A structured scratchpad for multi-step reasoning.

## Add it

```yaml
# workspace.yaml
mcp_servers:
- id: sequential-thinking
  transport: stdio
  command:
  - npx
  - -y
  - '@modelcontextprotocol/server-sequential-thinking'
  permission: readonly
  effects:
    sequentialthinking: read
```

```yaml
# a topology or archetype
skills:
  - pack:sequential-thinking    # every read skill below
```

Needs swarmkit-runtime **>=1.199.0**. Upstream: `npm @modelcontextprotocol/server-sequential-thinking`.

## Skills

### `sequential-thinking`

| | |
| --- | --- |
| tool | `sequentialthinking` |
| category | capability |
| effects | **read** |

**What it does.** Records and revises a chain of reasoning steps.

**Why you would want it.** Makes a model's plan explicit and revisable rather than buried in prose. The steps land in the run trace, so a wrong answer can be traced to the step that went wrong.

**When to grant it.** Most useful on a single capable agent doing hard analysis. Of limited value to a coordinator that only delegates.
