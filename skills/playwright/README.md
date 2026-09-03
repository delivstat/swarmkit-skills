# Playwright

Drive a real browser: navigate, click, fill, and read the page.

## Add it

```yaml
# workspace.yaml
mcp_servers:
- id: playwright
  transport: stdio
  command:
  - npx
  - -y
  - '@playwright/mcp@latest'
  permission: cautious
  effects:
    browser_snapshot: read
    browser_take_screenshot: read
    browser_console_messages: read
    browser_navigate: write
    browser_click: write
    browser_type: write
```

```yaml
# a topology or archetype
skills:
  - pack:playwright    # every read skill below
```

Needs swarmkit-runtime **>=1.199.0**. Upstream: `npm @playwright/mcp`.

## Skills

### `browser-snapshot`

| | |
| --- | --- |
| tool | `browser_snapshot` |
| category | capability |
| effects | **read** |

**What it does.** Returns the page's accessibility tree.

**Why you would want it.** The accessibility tree is the closest thing a page has to a semantic contract — far more stable than a screenshot and far cheaper than raw HTML.

**When to grant it.** This is the read primitive. Give it to any agent that inspects a page.

### `browser-navigate`

| | |
| --- | --- |
| tool | `browser_navigate` |
| category | capability |
| effects | **write** |

**What it does.** Navigates to a URL.

**Why you would want it.** Declared effects: write, because navigation can submit, log out or trigger a side effect.

**When to grant it.** Grant to agents that drive a flow, not to ones that only inspect.

### `browser-click`

| | |
| --- | --- |
| tool | `browser_click` |
| category | capability |
| effects | **write** |

**What it does.** Clicks an element.

**Why you would want it.** The action primitive. Everything an agent can do wrong on a website, it does through this.

**When to grant it.** Grant deliberately, and prefer a funnel gate on the node holding it.
