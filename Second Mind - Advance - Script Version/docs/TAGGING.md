# Tagging system

Minimal tags, high leverage. Use Obsidian frontmatter `tags:` or inline `#tag` (pick one style per vault and stay consistent).

## Dimensions

### Domain (what field?)

Examples: `#domain/genai`, `#domain/ml`, `#domain/systems`, `#domain/data`, `#domain/product`, `#domain/research`.

### Type (what shape of note?)

Examples: `#type/concept`, `#type/paper`, `#type/workflow`, `#type/idea`, `#type/project`, `#type/tooling`.

### State (where am I in learning?)

Examples: `#state/to-learn`, `#state/learning`, `#state/understood`, `#state/applied`.

## Rules

1. **At least one domain** on every processed wiki note.
2. **Exactly one type** per note (split if it mixes types).
3. **State** is optional on reference notes; **required** on concepts you are actively learning.
4. Prefer **3–6 tags total** per note; avoid tag sprawl.
5. Use `[[wikilinks]]` for concepts; use tags for facets (domain/type/state).

## LLM vs human

| Responsibility | Who |
|----------------|-----|
| Domain + type from content | LLM (suggest), human (confirm) |
| State | Human (LLM may guess `to-learn`—treat as draft) |
| Project-specific tags | Human |
| Renames / merges of tag vocabulary | Human (monthly) |

## Example frontmatter

```yaml
---
title: Low-Rank Adaptation (LoRA)
tags:
  - domain/genai
  - type/concept
  - state/understood
---
```
