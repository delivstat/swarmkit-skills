# Git

Read history, diffs and blame from a local repository.

## Add it

```yaml
# workspace.yaml
mcp_servers:
- id: git
  transport: stdio
  command:
  - uvx
  - mcp-server-git
  - --repository
  - ${SWARMKIT_GIT_REPO}
  permission: readonly
  effects:
    git_status: read
    git_diff: read
    git_log: read
    git_show: read
```

```yaml
# a topology or archetype
skills:
  - pack:git    # every read skill below
```

Needs swarmkit-runtime **>=1.199.0**. Upstream: `pypi mcp-server-git`.

## Skills

### `git-status`

| | |
| --- | --- |
| tool | `git_status` |
| category | capability |
| effects | **read** |

**What it does.** Shows the working tree status.

**Why you would want it.** Tells an agent what has changed before it changes more — the difference between a review of your diff and a review of the whole repository.

**When to grant it.** Give it to review and QA agents.

### `git-diff`

| | |
| --- | --- |
| tool | `git_diff` |
| category | capability |
| effects | **read** |

**What it does.** Returns the diff of the working tree or between refs.

**Why you would want it.** A diff is the smallest complete description of a change, which makes it the right input for any review skill.

**When to grant it.** Feed it to code-quality-review or security-scan rather than passing whole files.

### `git-log`

| | |
| --- | --- |
| tool | `git_log` |
| category | capability |
| effects | **read** |

**What it does.** Returns commit history.

**Why you would want it.** History answers *why* a line looks the way it does. An agent without it re-litigates decisions already made.

**When to grant it.** Useful for change-impact analysis and for writing release notes.
