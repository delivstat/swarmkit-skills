# Repo Report — a workspace built only from catalogue bundles

A working SwarmKit workspace whose every `mcp_servers` block was copied out of a bundle page and
pasted here unchanged. The swarm reads a repository and writes a short report about it: what it is,
how it is laid out, and what changed recently.

It is the showcase and it is a test. `scripts/check_contract.py` loads this with the real runtime on
every push, so a bundle whose published config SwarmKit cannot actually parse fails CI here — not in
somebody's terminal an hour after they copied it.

## Run it

Everything it needs runs without a credential.

```bash
export SWARMKIT_GIT_REPO=.        # the repository to report on
export SWARMKIT_FS_ROOT=.         # what the filesystem server may reach
export ANTHROPIC_API_KEY=...      # or edit the archetypes for another provider

pip install "swarmkit-runtime>=1.205.0"
swarmkit run examples/repo-report/ repo-report --input "Summarise this repository for a newcomer."
```

Three servers start: `git`, `filesystem`, `markitdown`.

## What it demonstrates

**Three bundles composing.** `git` for history, `filesystem` for layout, `markitdown` so a worker
can read a PDF or `.docx` it finds. Nothing in the server blocks was written by hand.

**Two permission tiers, on purpose.** `git` and `markitdown` are `readonly`; `filesystem` is
`cautious` because the same server that reads a file can write one. The effects map is what makes
that distinction enforceable rather than decorative — `readonly` denies `write_file` because the
bundle declares `write_file: write`, not because the runtime guessed from the name.

**An agent that cannot write, structurally.** `catalogue-reader` holds only read skills, and the
one write skill in the filesystem bundle is not copied into this workspace at all. A prompt asking
it to change a file cannot make that possible — which is the difference between a policy and a
request.

## Layout

```
workspace.yaml              three server blocks, copied verbatim from bundles
skills/                     the skill files, likewise copied
archetypes/
  report-writer.yaml        root: delegates, then writes the report
  catalogue-reader.yaml     worker: read-only, built from catalogue skills
topologies/
  repo-report.yaml          root → repo-reader + history-reader
```

Both archetypes are defined here rather than referencing SwarmKit's `reference/` set, so the
workspace stands alone. A fixture that depends on another repository's contents fails for reasons
that have nothing to do with the catalogue.
