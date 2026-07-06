# corpus/

Per-declaration annotation YAML files.

## Layout

```
corpus/<module-path>/<decl-name>.yaml
```

The `<module-path>` mirrors the Lean module path with `.` replaced by `/`.
For example, the declaration `LerayHopf.R3.rellich_seq_compact` lives at:

```
corpus/LerayHopf/R3/rellich_seq_compact.yaml
```

## Schema

See `docs/schemas/corpus.schema.json` for the full JSON Schema (draft-07).

Key fields:
- `name` — fully-qualified Lean declaration name
- `tier` — `full` (statement + proof + gap) or `gloss` (1–3 line role summary)
- `statement_ja` — Japanese translation of the mathematical statement
- `proof_ja` — Japanese proof narrative (required for `tier: full` theorems)
- `gap` — formalization gap assessment (`none | mild | large`)
- `chapter` — chapter assignment from `docs/schemas/chapters.yaml`
- `tags` — optional free-form tags

## Naming

Corpus files use the declaration's **simple name** (last component) as the filename.
The fully-qualified name is stored in the `name` field for join against `extracted/`.
