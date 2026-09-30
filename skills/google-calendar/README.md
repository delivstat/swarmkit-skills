# Google Calendar

Read Google Calendar events, list calendars, and check free/busy through Google's official
remote MCP server, over per-user OAuth. Sibling of the `gmail` bundle — same shape, calendar
surface.

## Add it

Remote MCP server + per-user OAuth credential; the workspace change is two blocks:

```yaml
# workspace.yaml
credentials:
  google-calendar:
    source: oauth
    config:
      endpoint: https://calendarmcp.googleapis.com/mcp/v1
      # `owner` is the identity the token is bound to. Set it to the account that will sign in
      # from the portal. A scheduled run needs a credential explicitly designated for unattended
      # use — see design/details/mcp-oauth.md.
      owner: you@example.com

mcp_servers:
- id: google-calendar
  transport: http
  endpoint: https://calendarmcp.googleapis.com/mcp/v1
  credentials_ref: google-calendar
  permission: readonly

# a topology or archetype
skills:
  - pack:google-calendar    # every read skill below
```

Then, in the portal: **Connections → Connect Google Calendar**. Google's OAuth flow runs, the
runtime stores the encrypted token, refreshes on use.

Needs swarmkit-runtime **>=1.259.0** (the per-user OAuth connections shipped in
delivstat/swarmkit#976 and #982). Upstream:
[Google Workspace Calendar MCP server](https://developers.google.com/workspace/calendar/api/guides/configure-mcp-server).

## What this bundle does NOT expose

Google's Calendar MCP exposes eight tools. Four are mutating: `create_event`, `update_event`,
`delete_event`, `respond_to_event`. This bundle exposes **only the four read-only tools**
(`list_calendars`, `list_events`, `get_event`, `suggest_time`).

The write side is deliberately deferred. A future `google-calendar-write` bundle will add them
behind `permission: cautious` with HITL gates when the approval-gate design work lands. Scheduling
or cancelling a meeting from an autonomous swarm is a larger-blast-radius action than reading
one, and the read + write mixture is not what a first release should be.

## Which server this points at

Two real options for a Google Calendar MCP server as of 2026:

- **Google's own remote MCP server** at `https://calendarmcp.googleapis.com/mcp/v1` (developer
  preview, part of the Google Workspace remote MCP suite). Implements MCP authorization spec
  revision 2026-07-28. First-party, no adapter. **This bundle defaults to it.**
- **Community self-hosted options** — [nspady/google-calendar-mcp](https://github.com/nspady/google-calendar-mcp)
  is the most-referenced; [j3k0/mcp-google-workspace](https://github.com/j3k0/mcp-google-workspace)
  bundles Gmail + Calendar in one server. Point the `endpoint` at your own instance if you'd
  rather self-host. Tool names may differ — check your chosen server's docs before adjusting the
  skill wiring.

## Skills

### `list-calendars`

| | |
| --- | --- |
| tool | `list_calendars` |
| category | capability |
| effects | **read** |

**What it does.** Lists the calendars the signed-in user has access to — their own primary
calendar plus every shared one they can read.

**Why you would want it.** What a swarm reaches for when it needs to know "which calendars are
in play" before drilling into events on a specific one. Useful for people who juggle work,
personal, and shared team calendars.

**When to grant it.** Whenever the agent needs to enumerate calendars. Often the first call a
calendar-aware agent makes.

### `list-events`

| | |
| --- | --- |
| tool | `list_events` |
| category | capability |
| effects | **read** |

**What it does.** Fetches events from a specific calendar over a time window.

**Why you would want it.** The primary reading tool — what a morning-brief-style swarm calls
for "what's on today and tomorrow" before ranking or prepping. Also what a meeting-density agent
uses when it wants to know if a day is booked solid before responding to a new invite.

**When to grant it.** Whenever the agent needs the actual events, not just the calendars.
Almost always alongside `list-calendars` for a multi-calendar setup.

### `get-event`

| | |
| --- | --- |
| tool | `get_event` |
| category | capability |
| effects | **read** |

**What it does.** Fetches a single calendar event by id — attendees, description, conferencing
links, recurrence details.

**Why you would want it.** Useful when the agent already knows which event it cares about (from
a list, a webhook, a search result) and wants the full picture without paging through a list
response.

**When to grant it.** For point-lookup work — usually alongside `list-events` in the same
agent.

### `suggest-time`

| | |
| --- | --- |
| tool | `suggest_time` |
| category | capability |
| effects | **read** |

**What it does.** Asks Google Calendar for candidate meeting slots given a set of attendees, a
desired duration, and a search window. **Read-only** — returns suggestions, does not create the
meeting.

**Why you would want it.** For meeting-prep agents that want to answer "when could we all get
together this week" without booking anything. The scheduling side of a "let me draft a response
proposing times" workflow.

**When to grant it.** Alongside `list-events` and `get-event` for any agent that reasons about
scheduling. Independent of the write-side `create_event` tool this bundle deliberately does not
expose — suggesting is not scheduling.
