# Installation

1. Add this repo as a HACS custom repository (Integration category).
2. Install **Jinja Files**.
3. Restart Home Assistant.
4. Drop `*.j2` files under `<config>/templates/`.
5. Call the `jinja_files.render` service.

## Automate it (nightly)

```yaml
trigger:
  - platform: time
    at: '03:00:00'
action:
  - service: jinja_files.render
```
