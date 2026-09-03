# Time

Current time and timezone conversion.

## Add it

```yaml
# workspace.yaml
mcp_servers:
- id: time
  transport: stdio
  command:
  - uvx
  - mcp-server-time
  permission: readonly
  effects:
    get_current_time: read
    convert_time: read
```

```yaml
# a topology or archetype
skills:
  - pack:time    # every read skill below
```

Needs swarmkit-runtime **>=1.199.0**. Upstream: `pypi mcp-server-time`.

## Skills

### `current-time`

| | |
| --- | --- |
| tool | `get_current_time` |
| category | capability |
| effects | **read** |

**What it does.** Returns the current time in a timezone.

**Why you would want it.** A model has no clock and will confidently invent one. Any agent reasoning about schedules, deadlines or recency needs this or it makes things up.

**When to grant it.** Cheap enough to grant by default to agents that mention dates.

### `convert-time`

| | |
| --- | --- |
| tool | `convert_time` |
| category | capability |
| effects | **read** |

**What it does.** Converts a time between timezones.

**Why you would want it.** Timezone arithmetic is a classic quiet-failure: plausible, wrong, and nobody checks.

**When to grant it.** Grant alongside current-time for anything scheduling-related.
