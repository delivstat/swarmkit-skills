# MarkItDown

Convert a PDF, Office document, image or web page to markdown.

One tool, and it is the one that unblocks every knowledge task where the source is not already
text. Models reason over markdown; the world ships PDFs and .docx.

Reads a URI — `http:`, `https:`, `file:` or `data:` — so a `file:` URI reaches anything the server
process can read. Scope that with the process, not with the prompt.

Optional extras upstream (audio transcription, some image handling) want `ffmpeg` and, for image
descriptions, a model endpoint. The base install converts documents without either.

## Add it

```yaml
# workspace.yaml
mcp_servers:
- id: markitdown
  transport: stdio
  command:
  - uvx
  - markitdown-mcp
  permission: readonly
  effects:
    convert_to_markdown: read
```

```yaml
# a topology or archetype
skills:
  - pack:markitdown    # every read skill below
```

Needs swarmkit-runtime **>=1.199.0**. Upstream: `pypi markitdown-mcp`.

## Skills

### `convert-to-markdown`

| | |
| --- | --- |
| tool | `convert_to_markdown` |
| category | capability |
| effects | **read** |

**What it does.** Converts a document at a URI — PDF, Word, PowerPoint, Excel, HTML, image or CSV — to markdown.

**Why you would want it.** The alternative is an agent that cannot read the attachment the whole task is about. Markdown preserves the headings and tables that carry the structure, which plain text extraction throws away.

**When to grant it.** Give it to any agent whose input arrives as a file. Effect is **read**: it converts and returns, it never writes the result anywhere.
