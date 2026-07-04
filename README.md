# Jinja Files

[![Built with Claude Code](https://img.shields.io/badge/Built%20with%20Claude%20Code-D97757?style=for-the-badge&logo=claude&logoColor=white)](https://claude.ai/code)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-41BDF5?style=for-the-badge&logo=homeassistant&logoColor=white)](https://www.home-assistant.io/)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5?style=for-the-badge&logo=homeassistantcommunitystore&logoColor=white)](https://hacs.xyz/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-FFDD00?style=for-the-badge&logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/saya6k)

A Home Assistant custom integration that renders **every `.j2` file under `<config>/templates/`** into its corresponding location, using HA state, installed add-ons, and HACS components as template context.

Forked from [custom-components/readme](https://github.com/custom-components/readme) (Joakim Sørensen / @ludeeus), generalized so it isn't limited to `README.md`. Also includes fixes for upstream issues [#116](https://github.com/custom-components/readme/issues/116) (`hass.components` removal) and [#104](https://github.com/custom-components/readme/issues/104) (Supervisor addons API deprecation).

## How it works

```
<config>/templates/README.md.j2              ──▶  <config>/README.md
<config>/templates/docs/index.md.j2          ──▶  <config>/docs/index.md
<config>/templates/docs/platform/network.md.j2 ──▶ <config>/docs/platform/network.md
```

Source path's `.j2` suffix is stripped; everything else (directory structure, filename, extension) maps 1:1.

## Template context

Each template is rendered with these variables (plain Jinja2 — **no HA template helpers like `now()`**, only what's listed below):

| Variable | Type | Description |
| --- | --- | --- |
| `states` | `AllStates` | Same as HA templates — `states('sensor.foo')`, `states.sensor`, `states \| count`, etc. |
| `addons` | `list[dict]` | Installed Supervisor add-ons. Keys include `name`, `slug`, `version`, `state`, `version_latest`, `update_available`, `repository`, `description`. |
| `hacs_components` | `list[dict]` | HACS-downloaded repositories. Keys include `category` (`integration` / `plugin` / `theme` / …), `name`, `documentation`, `description`, `full_name`. |
| `custom_components` | `list[dict]` | Loaded custom integrations. Keys: `domain`, `name`, `documentation`, `version`, `codeowners`. |

## Service

```yaml
service: jinja_files.render
```

Optional parameter to render a single template:

```yaml
service: jinja_files.render
data:
  path: docs/index.md.j2     # relative to templates/
```

By default, outputs that already exist are **skipped**. Pass `override: true` to overwrite them:

```yaml
service: jinja_files.render
data:
  override: true
```

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=saya6k&repository=hacs-jinja-files&category=integration)

1. Add this repo as a HACS custom repository (Integration category).
2. Install **Jinja Files**.
3. Restart Home Assistant.
4. Drop `*.j2` files under `<config>/templates/`.
5. Call the service.

Automate it (e.g. nightly):

```yaml
trigger:
  - platform: time
    at: '03:00:00'
action:
  - service: jinja_files.render
```

## Differences from upstream `readme`

| Aspect | `readme` | `jinja_files` |
| --- | --- | --- |
| Output | only `templates/README.j2` → `README.md` | every `*.j2` under `templates/` → relative path with `.j2` stripped |
| Filename convention | hardcoded | strip `.j2` extension |
| Single-file mode | n/a | `path:` service param |
| Supervisor API | `hass.components.hassio` (broken on modern HA) | `homeassistant.components.hassio.get_addons_info` |
| Addon list source | `supervisor_info.addons` (deprecated) | `get_addons_info(hass)` |
| Lovelace YAML conversion | optional | removed (out of scope) |

## License

MIT. See [LICENSE](LICENSE).
