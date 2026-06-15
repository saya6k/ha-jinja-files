# Usage

## Template context

Each template is rendered with these variables (plain Jinja2 — **no HA template helpers like `now()`**, only what's listed below):

| Variable | Type | Description |
| --- | --- | --- |
| `states` | `AllStates` | Same as HA templates — `states('sensor.foo')`, `states.sensor`, `states \| count`, etc. |
| `addons` | `list[dict]` | Installed Supervisor add-ons. Keys include `name`, `slug`, `version`, `state`, `version_latest`, `update_available`, `repository`, `description`. |
| `hacs_components` | `list[dict]` | HACS-downloaded repositories. Keys include `category` (`integration` / `plugin` / `theme` / …), `name`, `documentation`, `description`, `full_name`. |
| `custom_components` | `list[dict]` | Loaded custom integrations. Keys: `domain`, `name`, `documentation`, `version`, `codeowners`. |

## Service

Render every `.j2` file under `templates/`:

```yaml
service: jinja_files.render
```

Render a single template:

```yaml
service: jinja_files.render
data:
  path: docs/index.md.j2     # relative to templates/
```

Render several templates with a wildcard (`*`, `?`, `[...]`):

```yaml
service: jinja_files.render
data:
  path: docs/*.md.j2         # every .md.j2 under templates/docs/
```
