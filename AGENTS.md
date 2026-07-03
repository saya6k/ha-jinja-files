# Repository agent instructions

This file is the **source of truth** for agent guidance in this repo.
`CLAUDE.md` at the repo root is a symlink to it — edit this file, not the
symlink.

Guidance for AI coding agents. **Keep this file under ~100 lines** —
describe the *current shape* only. *Why* lives under `notes/` (gitignored;
AGENTS may name files there, README/CHANGELOG must not). CHANGELOG carries
*what changed*.

## What this repo is

A Home Assistant **custom integration** (HACS, category *Integration*) named
**Jinja Files** (domain `jinja_files`). It renders **every `.j2` file under
`<config>/templates/`** to its corresponding output path, with HA state,
Supervisor add-ons, HACS repos, and loaded custom integrations as template
context.

Forked from [custom-components/readme](https://github.com/custom-components/readme)
(Joakim Sørensen / @ludeeus), generalized beyond `README.md` and patched for
upstream issues [#116](https://github.com/custom-components/readme/issues/116)
(`hass.components` removal) and
[#104](https://github.com/custom-components/readme/issues/104) (Supervisor
addons API deprecation).

## Layout

```
custom_components/jinja_files/   manifest.json, __init__.py (render service), helpers
hacs.json                        HACS metadata
docs/{en,ko}/                    Zensical doc sources
zensical.{en,ko}.toml            Zensical site config
```

## How it works (invariants)

- **Path mapping is 1:1 with the `.j2` suffix stripped.**
  `templates/docs/index.md.j2 → docs/index.md`. Directory structure,
  filename, and extension otherwise map exactly. Don't introduce
  filename-rewriting heuristics — that was the upstream's mistake.
- **Plain Jinja2 only.** Templates get `states`, `addons`, `hacs_components`,
  `custom_components` — **no HA template helpers** (`now()`, etc.). Don't
  widen the context to the full HA template environment.
- **Supervisor data comes from `homeassistant.components.hassio.get_addons_info(hass)`**
  — not the removed `hass.components.hassio` / deprecated
  `supervisor_info.addons`. Keep using the supported API.
- **Single service: `jinja_files.render`** with optional `path:` (relative to
  `templates/`) to render just one file. No Lovelace YAML conversion (dropped
  from upstream as out of scope) — don't re-add it.

## Sanity checks before release

- Integration loads in a HA dev instance; `jinja_files.render` appears as a
  service.
- A `templates/README.md.j2` referencing `states`, `addons`,
  `hacs_components` renders to `README.md` with values filled in.
- `path:` parameter renders only the named template.

## Don'ts

- **Don't reintroduce the `README.md`-only assumption** — the whole point of
  the fork is rendering arbitrary `*.j2` trees.
- **Don't call deprecated/removed Supervisor APIs** — that's exactly the
  upstream breakage this fork fixes.

## License

MIT (`LICENSE`).
