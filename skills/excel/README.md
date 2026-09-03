# Excel

Read and write .xlsx workbooks — data, formulas, formatting — with no Excel installed.

Spreadsheets are how most organisations actually hold their data, and a swarm that cannot read one
is a swarm that cannot see the input. This writes them too, which is why it is `cautious`.

Runs on `openpyxl`, so no Excel and no Windows. It operates on files by path — restrict what the
process can reach, and set `EXCEL_FILES_PATH` if you want it confined to one directory.

Twenty-five tools upstream, six here. Charts, pivot tables and merge operations are left out on
purpose: an agent handed twenty-five ways to change a workbook makes worse choices than one handed
six, and the rest are a paste away for anyone who needs them.

## Add it

```yaml
# workspace.yaml
mcp_servers:
- id: excel
  transport: stdio
  command:
  - uvx
  - excel-mcp-server
  - stdio
  permission: cautious
  effects:
    read_data_from_excel: read
    get_workbook_metadata: read
    validate_excel_range: read
    validate_formula_syntax: read
    write_data_to_excel: write
    create_workbook: write
    apply_formula: write
    format_range: write
```

```yaml
# a topology or archetype
skills:
  - pack:excel    # every read skill below
```

Writes are never in that. Name them:

```yaml
skills:
  - pack:excel
  - excel-write-data
  - excel-apply-formula
```

Needs swarmkit-runtime **>=1.199.0**. Upstream: `pypi excel-mcp-server`.

## Skills

### `excel-read-data`

| | |
| --- | --- |
| tool | `read_data_from_excel` |
| category | capability |
| effects | **read** |

**What it does.** Reads a cell range from a worksheet.

**Why you would want it.** The read half, and usually the only half you want. Extraction and reconciliation tasks read a sheet and write nothing.

**When to grant it.** Safe under `permission: readonly` and carried by `pack:excel`. Grant it freely.

### `excel-workbook-metadata`

| | |
| --- | --- |
| tool | `get_workbook_metadata` |
| category | capability |
| effects | **read** |

**What it does.** Returns the sheets, used ranges and structure of a workbook.

**Why you would want it.** A workbook is not a table — it is several, at unpredictable offsets, often with a title row. Reading A1:Z100 and hoping is how an agent reports confident nonsense.

**When to grant it.** Call it before any read. Grant it wherever you grant `excel-read-data`.

### `excel-validate-range`

| | |
| --- | --- |
| tool | `validate_excel_range` |
| category | capability |
| effects | **read** |

**What it does.** Checks that a range exists and is well-formed before anything touches it.

**Why you would want it.** Turns a silently empty read into an error. A range that is off by one sheet returns nothing, which looks exactly like a sheet with no data.

**When to grant it.** Cheap insurance ahead of a write.

### `excel-validate-formula`

| | |
| --- | --- |
| tool | `validate_formula_syntax` |
| category | capability |
| effects | **read** |

**What it does.** Validates a formula's syntax without applying it.

**Why you would want it.** Lets an agent check its own work before writing something that renders as `#NAME?` to whoever opens the file next.

**When to grant it.** Grant it with `excel-apply-formula`, never instead of it.

### `excel-write-data`

| | |
| --- | --- |
| tool | `write_data_to_excel` |
| category | capability |
| effects | **write** |

**What it does.** Writes values into a cell range.

**Why you would want it.** The point of a report-producing agent. Also the call that overwrites somebody's data.

**When to grant it.** Effect is **write**: refused under `readonly`, never in a `pack:` grant, granted by name to one agent.

### `excel-apply-formula`

| | |
| --- | --- |
| tool | `apply_formula` |
| category | capability |
| effects | **write** |

**What it does.** Writes a formula into a cell.

**Why you would want it.** A formula keeps recalculating after the agent has gone, which is the difference between a snapshot and a working sheet.

**When to grant it.** Effect is **write**, and it deserves more suspicion than a plain value: a wrong formula propagates to every cell that references it. Validate first.
