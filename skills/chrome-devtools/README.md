# Chrome DevTools

Diagnose a page: performance traces, console errors, network requests and a Lighthouse audit.

Second only to Playwright in every ranking, and it earns the place by answering a different
question. Playwright drives a page; DevTools explains one. The skills here are deliberately the
tools Playwright has no equivalent for — traces, console, network, Lighthouse — so a workspace can
hold both bundles without an agent facing two ways to click a button.

Needs Chrome or Chromium on the machine. It drives your real browser, so treat it as it treats
itself: `cautious`, not `readonly`.

## Add it

```yaml
# workspace.yaml
mcp_servers:
- id: chrome-devtools
  transport: stdio
  command:
  - npx
  - -y
  - chrome-devtools-mcp@latest
  permission: cautious
  effects:
    take_snapshot: read
    list_console_messages: read
    get_console_message: read
    list_network_requests: read
    get_network_request: read
    lighthouse_audit: read
    performance_analyze_insight: read
    navigate_page: write
    performance_start_trace: write
    performance_stop_trace: write
```

```yaml
# a topology or archetype
skills:
  - pack:chrome-devtools    # every read skill below
```

Writes are never in that. Name them:

```yaml
skills:
  - pack:chrome-devtools
  - cdt-performance-trace
```

Needs swarmkit-runtime **>=1.199.0**. Upstream: `npm chrome-devtools-mcp`.

## Skills

### `cdt-console-messages`

| | |
| --- | --- |
| tool | `list_console_messages` |
| category | capability |
| effects | **read** |

**What it does.** Lists every console message on the page since the last navigation.

**Why you would want it.** A page that renders correctly and logs a stack trace on every keystroke is broken in a way no screenshot shows. This is the cheapest signal that something is wrong.

**When to grant it.** Give it to any agent reviewing a front-end change — it costs one call and frequently ends the investigation.

### `cdt-network-requests`

| | |
| --- | --- |
| tool | `list_network_requests` |
| category | capability |
| effects | **read** |

**What it does.** Lists the recent network requests, with status and timing.

**Why you would want it.** Distinguishes *the page is slow* from *one request is slow*, and finds the 404 for an asset that fails silently.

**When to grant it.** Useful for performance work and for confirming an API is actually being called with what you think.

### `cdt-lighthouse-audit`

| | |
| --- | --- |
| tool | `lighthouse_audit` |
| category | capability |
| effects | **read** |

**What it does.** Runs a Lighthouse audit for accessibility, SEO and best practices.

**Why you would want it.** Turns *does this page look fine* into a scored report against published criteria, which is a claim a reviewer can check rather than a matter of taste.

**When to grant it.** Grant it to review agents on front-end work. Not for every run — an audit is slow.

### `cdt-performance-trace`

| | |
| --- | --- |
| tool | `performance_start_trace` |
| category | capability |
| effects | **write** |

**What it does.** Starts a performance trace, reloading the page to capture it.

**Why you would want it.** Core Web Vitals are measured, not guessed. This is the measurement.

**When to grant it.** Effect is **write** because it navigates: it reloads the page, so it is refused under `permission: readonly` and never rides in a `pack:` grant.

### `cdt-analyze-insight`

| | |
| --- | --- |
| tool | `performance_analyze_insight` |
| category | capability |
| effects | **read** |

**What it does.** Explains one insight from a captured trace in detail.

**Why you would want it.** A trace is thousands of events. This is the tool that turns it into a sentence about what to fix.

**When to grant it.** Pair it with `cdt-performance-trace` — the trace is the raw material and this reads it.
