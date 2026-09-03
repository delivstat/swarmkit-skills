# Filesystem

Read, write and search files under a directory you nominate.

## Add it

```yaml
# workspace.yaml
mcp_servers:
- id: filesystem
  transport: stdio
  command:
  - npx
  - -y
  - '@modelcontextprotocol/server-filesystem'
  - ${SWARMKIT_FS_ROOT}
  permission: cautious
  effects:
    read_file: read
    read_multiple_files: read
    list_directory: read
    directory_tree: read
    search_files: read
    get_file_info: read
    write_file: write
    edit_file: write
    create_directory: write
    move_file: write
```

```yaml
# a topology or archetype
skills:
  - pack:filesystem    # every read skill below
```

Needs swarmkit-runtime **>=1.199.0**. Upstream: `npm @modelcontextprotocol/server-filesystem`.

## Skills

### `fs-read-file`

| | |
| --- | --- |
| tool | `read_file` |
| category | capability |
| effects | **read** |

**What it does.** Reads one file and returns its contents.

**Why you would want it.** An agent that can read the repository it is reasoning about stops guessing at file contents, which is the single largest source of confident-but-wrong output.

**When to grant it.** Give it to any agent that reviews, summarises or edits code.

### `fs-list-directory`

| | |
| --- | --- |
| tool | `list_directory` |
| category | capability |
| effects | **read** |

**What it does.** Lists the entries in one directory.

**Why you would want it.** Cheaper than a tree walk when the agent only needs to orient — and it keeps a large repository from filling the context window.

**When to grant it.** Pair with fs-read-file so the agent can find a file before reading it.

### `fs-search-files`

| | |
| --- | --- |
| tool | `search_files` |
| category | capability |
| effects | **read** |

**What it does.** Finds files matching a pattern under a root.

**Why you would want it.** Search is how an agent locates the thing it was asked about. Without it every task starts with the agent asking you where something is.

**When to grant it.** Give it to any agent working in a repository it did not author.

### `fs-write-file`

| | |
| --- | --- |
| tool | `write_file` |
| category | capability |
| effects | **write** |

**What it does.** Writes a file, creating or replacing it.

**Why you would want it.** The write half. Declared effects: write, so `permission: readonly` denies it and a bulk `pack:` grant never carries it.

**When to grant it.** Grant deliberately, to agents that are meant to change things. Consider a funnel gate on the node that holds it.
