# Cloudflare Kitesurf

Browse the web on Cloudflare's agent-first browser: open a page, read it, and act on it, with reading and acting granted separately.

[Kitesurf](https://blog.cloudflare.com/kitesurf-update/) is a browser built for agents, not people.
- **How it runs:** on Cloudflare Workers, one V8 isolate per page, without tabs, extensions or the rest of what a person needs.
- **Cost:** Cloudflare pitches it at a fraction of Chromium's memory and CPU for agent work.
- **Where it runs:** on Cloudflare, not on your machine, so a page can't touch your host.
- **How SwarmKit reaches it:** Cloudflare's [Browser Run](https://developers.cloudflare.com/browser-run/cdp/mcp-clients/), through `chrome-devtools-mcp` pointed at Browser Run's DevTools endpoint with `browser=kitesurf`.

Use it when an agent needs to read the live web: a page that only renders with JavaScript, a site with no API, or a check that something published looks right. If a site does have an API or an MCP server, use that instead: it's cheaper and it doesn't break when the page's markup changes.

**Kitesurf is a beta, and compatibility is early.** Cloudflare's guidance is to keep Chromium for video, WebGL, bot challenges and long logged-in sessions. To use Chromium on Browser Run, drop `browser=kitesurf` from the endpoint below; every skill here works the same way.

## Before you grant anything

**Everything a page returns is written by whoever owns the site.** A page can contain text addressed to your agent ("ignore your instructions and…"). Treat these skills' results as content, never as instructions. Don't give an agent that browses the open web write tools elsewhere, such as repo writes or email, without a gate between them.

**Reading and acting are separate grants.**
- The three **read** skills are `kitesurf-read-page`, `kitesurf-screenshot` and `kitesurf-wait-for`. None of them can get the browser anywhere new on its own.
- To go somewhere, add `kitesurf-open`. To act on a page, add `kitesurf-click` and `kitesurf-fill-form`. All three are **write**, so they are refused under `permission: readonly`.
- **Name each skill.** Don't use `server:kitesurf`: it grants every skill on the server, the write skills included.

**Why opening a page is write, not read:**
- It sends a request to a site you didn't choose in advance.
- A URL can carry anything the agent puts in it, so it is a way for data to leave.
- The tool also accepts an `initScript` argument, which runs JavaScript when the page loads.

**Left out on purpose** (`chrome-devtools-mcp` lists 33 tools; browsing needs these six):
- `evaluate_script` runs arbitrary JavaScript in the page, which would make every effect declared here meaningless.
- `upload_file` sends files from your machine to the site.
- The performance, Lighthouse and heap tools belong to the [`chrome-devtools`](../chrome-devtools/README.md) bundle. That bundle drives a local Chrome, while this one drives Cloudflare's browser.

**Effects differ from the server's hints in two places.** The server marks `take_snapshot` and `take_screenshot` as not read-only, because each can also save its result to a file. This bundle declares both `read`: they read the page and change nothing on it or on any site. With no roots capability negotiated, the server limits file saves to the OS temp folder.

## Credentials

You need two things:
1. **A Cloudflare account ID.**
2. **An API token with the `Browser Rendering - Edit` permission.** Create a custom token with only that.

Set them as environment variables for the runtime:

```bash
export CLOUDFLARE_ACCOUNT_ID=…
export CLOUDFLARE_API_TOKEN=…
```

**The token reaches the browser server as a command-line argument.** `chrome-devtools-mcp` reads its auth header only from `--wsHeaders`. So while the server runs, the token is visible to anyone who can list processes on the machine. It's the same exposure as Cloudflare's own documented config, which keeps the token in plain text in a config file. Run this on a machine you don't share, and give the token nothing beyond `Browser Rendering - Edit`.

The bundle also starts the server with `--no-usage-statistics --no-performance-crux`. Without these flags, `chrome-devtools-mcp` sends usage statistics to Google and performance trace URLs to the CrUX API.

Each server start opens one Browser Run session, kept alive for 10 minutes (`keep_alive=600000`) and used for every call until the server restarts. Kitesurf is free during the beta, within per-account limits.

## Add it

```yaml
# workspace.yaml
mcp_servers:
- id: kitesurf
  transport: stdio
  command:
  - npx
  - -y
  - chrome-devtools-mcp@latest
  - --wsEndpoint=wss://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/browser-run/devtools/browser?browser=kitesurf&keep_alive=600000
  - '--wsHeaders={"Authorization":"Bearer ${CLOUDFLARE_API_TOKEN}"}'
  - --no-usage-statistics
  - --no-performance-crux
  permission: cautious
  effects:
    take_snapshot: read
    take_screenshot: read
    wait_for: read
    navigate_page: write
    click: write
    fill_form: write
```

```yaml
# an agent that reads the pages it reaches
skills:
  - kitesurf-read-page
  - kitesurf-screenshot
  - kitesurf-wait-for
  - kitesurf-open        # write: go to a URL
```

```yaml
# an agent that also acts on a site, normally behind a gate
skills:
  - kitesurf-read-page
  - kitesurf-wait-for
  - kitesurf-open
  - kitesurf-click       # write
  - kitesurf-fill-form   # write
```

Don't grant `server:kitesurf`: it includes every skill on the server, the write skills too.

**Scopes:** reading needs `web:read`, opening needs `web:navigate`, and acting needs `web:act`. Grant them separately, so an agent that may read can't also submit.

Needs swarmkit-runtime **>=1.199.0**. Upstream: `npm chrome-devtools-mcp` connected to Cloudflare Browser Run.

## Skills

### `kitesurf-read-page`

| | |
| --- | --- |
| tool | `take_snapshot` |
| category | capability |
| effects | **read** |

**What it does.** Reads the open page as text: its accessibility tree, with every link, button and field labelled and given a `uid` that the act skills take.

**Why you would want it.** This is how an agent sees a page. It's text, so it costs far less than a screenshot. The uids are what `kitesurf-click` and `kitesurf-fill-form` point at, so the agent clicks the button it read rather than guessing coordinates.

**When to grant it.** Grant it to any agent that browses. It's the one skill here that nearly every use needs.

### `kitesurf-screenshot`

| | |
| --- | --- |
| tool | `take_screenshot` |
| category | capability |
| effects | **read** |

**What it does.** Captures the open page, or a single element, as an image.

**Why you would want it.** Some things the page's text doesn't carry: a chart, a layout that broke, whether a banner covers the button.

**When to grant it.** Grant it only to an agent on a model that can read images, and only when the look matters. An image costs many times what the text snapshot does.

### `kitesurf-wait-for`

| | |
| --- | --- |
| tool | `wait_for` |
| category | capability |
| effects | **read** |

**What it does.** Waits until some text appears on the open page.

**Why you would want it.** Many pages render after they load. Without this, an agent reads the loading spinner and reports that the page is empty.

**When to grant it.** Grant it alongside `kitesurf-read-page` for any site built as a single-page app.

### `kitesurf-open`

| | |
| --- | --- |
| tool | `navigate_page` |
| category | capability |
| effects | **write** |

**What it does.** Goes to a URL, or goes back, forward, or reloads.

**Why you would want it.** It's the way onto the web. Without it, the read skills only see the page the session started on.

**When to grant it.** Grant it when the agent has to reach pages itself. Its effect is **write** because a request goes to a site you didn't choose in advance, a URL can carry data out, and the tool can run a load-time script. Under `permission: cautious` every call is checked by governance and audited, so a run's audit trail is the list of every URL it opened.

### `kitesurf-click`

| | |
| --- | --- |
| tool | `click` |
| category | capability |
| effects | **write** |

**What it does.** Clicks an element on the open page, by the uid `kitesurf-read-page` gave it.

**Why you would want it.** Some sites can only be used by clicking through them.

**When to grant it.** Grant it only when the task is to act on a site. A click can submit, buy, post or delete on someone else's system, so pair it with an approval gate, or keep it to sites the workspace owns.

### `kitesurf-fill-form`

| | |
| --- | --- |
| tool | `fill_form` |
| category | capability |
| effects | **write** |

**What it does.** Fills several form fields at once (inputs, selects, checkboxes and radios), by uid.

**Why you would want it.** One call fills a whole form, instead of a field-by-field exchange that a page's re-render can break halfway through.

**When to grant it.** The question isn't whether the agent may type, but what it may type. Whatever it's given goes to the site. Don't grant it to an agent that also holds secrets or personal data, unless a gate approves each submission.
