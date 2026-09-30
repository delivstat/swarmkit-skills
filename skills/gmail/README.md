# Gmail

Read Gmail threads and messages through Google's official remote MCP server, over per-user OAuth.

## Add it

The Gmail bundle uses a **remote** MCP server and a **per-user OAuth** credential — two things
no bundle in this catalogue used before it. The workspace change is two blocks, not one: a
credential the token attaches to, and the server the credential guards.

```yaml
# workspace.yaml
credentials:
  gmail:
    source: oauth
    config:
      endpoint: https://gmailmcp.googleapis.com/mcp/v1
      # `owner` is the identity the token is bound to. Set it to the account that will sign in
      # from the portal (`serve` resolves it via /whoami). A scheduled run needs a credential
      # explicitly designated for unattended use — see design/details/mcp-oauth.md.
      owner: you@example.com

mcp_servers:
- id: gmail
  transport: http
  endpoint: https://gmailmcp.googleapis.com/mcp/v1
  credentials_ref: gmail
  permission: readonly

# a topology or archetype
skills:
  - pack:gmail    # every read skill below
```

Then, in the portal: **Connections → Connect Gmail**. The runtime completes Google's OAuth flow,
stores the encrypted token in its own credential store, and refreshes on use. Every subsequent
run of a topology that consumes `pack:gmail` picks up the live token without further prompting.

Needs swarmkit-runtime **>=1.259.0** (the per-user OAuth connections shipped in #976 and #982).
Upstream: [Google Workspace remote MCP servers](https://developers.google.com/workspace/guides/configure-mcp-servers).

## What this bundle does NOT expose

Google's Gmail MCP server exposes ten tools, including some that mutate state (`create_draft`,
`label_message`, `unlabel_thread`, `label_thread`, `unlabel_message`). This bundle exposes **only
the three read-only tools** needed for the search-then-read workflow that most agents want.

The write-side tools are deliberately deferred: sending or labelling from an autonomous swarm is
a larger-blast-radius action, and shipping it before the approval-gate design work is done would
be handing a foot-gun over a fence. A future bundle (`gmail-write`) will add them behind a
`permission: cautious` tier with HITL gates. This bundle stays `readonly` for that reason.

## Which server this points at

Two real options for a Gmail MCP server as of 2026:

- **Google's own remote MCP server** at `https://gmailmcp.googleapis.com/mcp/v1` (developer
  preview, August 2026). Implements the MCP authorization spec revision 2026-07-28, aligned
  with OAuth 2 + OpenID Connect. First-party, no adapter. **This bundle defaults to it.**
- **Community self-hosted options** — [GongRzhe/Gmail-MCP-Server](https://github.com/GongRzhe/Gmail-MCP-Server),
  [jasonsum/gmail-mcp-server](https://github.com/jasonsum/gmail-mcp-server). Point the `endpoint`
  at your own instance if you'd rather self-host or need a tool Google's preview server does not
  yet expose. The three skills below all use standard-shaped tool names that community servers
  also implement, but names may differ — check your chosen server's docs.

## Skills

### `search-threads`

| | |
| --- | --- |
| tool | `search_threads` |
| category | capability |
| effects | **read** |

**What it does.** Searches the signed-in user's Gmail using Gmail's own search syntax and returns
matching thread ids.

**Why you would want it.** This is what a swarm does when it wants "recent emails about X" or
"everything from Y this week." Gmail's search syntax is expressive; the tool passes it through
untouched.

**When to grant it.** Give it to any agent that needs to find email context. It reads the user's
mail — think about that before granting it to an agent that also has an outbound channel it
could quote email content into.

### `get-thread`

| | |
| --- | --- |
| tool | `get_thread` |
| category | capability |
| effects | **read** |

**What it does.** Fetches a full Gmail thread by id — every message in the conversation, in
order, with headers and body.

**Why you would want it.** Paired with `search-threads`, this is the "read the whole
conversation" step before an agent decides what to do about it. Threads matter for email
because a reply is meaningless without the message it replied to.

**When to grant it.** Whenever the agent needs the actual message contents, not just ids. Almost
always alongside `search-threads`.

### `get-message`

| | |
| --- | --- |
| tool | `get_message` |
| category | capability |
| effects | **read** |

**What it does.** Fetches a single Gmail message by id — headers, body, attachment metadata.

**Why you would want it.** Useful when an agent already knows which message it cares about
(from a search result, a webhook, a prior scan) and wants that one message without pulling the
whole thread.

**When to grant it.** For point-lookup work. If an agent is doing search-then-read, `get-thread`
is usually the better choice — an isolated message often reads meaninglessly without its
predecessors.
