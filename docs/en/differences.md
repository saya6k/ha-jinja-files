# Differences from upstream `readme`

| Aspect | `readme` | `jinja_files` |
| --- | --- | --- |
| Output | only `templates/README.j2` → `README.md` | every `*.j2` under `templates/` → relative path with `.j2` stripped |
| Filename convention | hardcoded | strip `.j2` extension |
| Single-file mode | n/a | `path:` service param |
| Supervisor API | `hass.components.hassio` (broken on modern HA) | `homeassistant.components.hassio.get_addons_info` |
| Addon list source | `supervisor_info.addons` (deprecated) | `get_addons_info(hass)` |
| Lovelace YAML conversion | optional | removed (out of scope) |
