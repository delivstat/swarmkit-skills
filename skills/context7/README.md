# Context7

Up-to-date documentation for a library, fetched on demand.

## Add it

```yaml
# workspace.yaml
mcp_servers:
- id: context7
  transport: stdio
  command:
  - npx
  - -y
  - '@upstash/context7-mcp@latest'
  permission: readonly
  effects:
    resolve-library-id: read
    get-library-docs: read
```

```yaml
# a topology or archetype
skills:
  - pack:context7    # every read skill below
```

Needs swarmkit-runtime **>=1.199.0**. Upstream: `npm @upstash/context7-mcp`.

## Skills

### `resolve-library-id`

| | |
| --- | --- |
| tool | `resolve-library-id` |
| category | capability |
| effects | **read** |

**What it does.** Finds the library id for a package name.

**Why you would want it.** Names are ambiguous; ids are not. This is the lookup step before fetching docs.

**When to grant it.** Always granted together with library-docs — one is useless without the other.

### `library-docs`

| | |
| --- | --- |
| tool | `query-docs` |
| category | capability |
| effects | **read** |

**What it does.** Fetches current documentation for a library.

**Why you would want it.** A model's knowledge of a fast-moving library is as old as its training data. This is the cheapest available fix for confidently-wrong API usage.

**When to grant it.** Give it to any agent writing code against third-party libraries.
