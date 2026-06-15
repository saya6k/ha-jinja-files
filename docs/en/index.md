# Jinja Files

A Home Assistant custom integration that renders **every `.j2` file under `<config>/templates/`** into its corresponding location, using HA state, installed add-ons, and HACS components as template context.

Forked from [custom-components/readme](https://github.com/custom-components/readme) (Joakim Sørensen / @ludeeus), generalized so it isn't limited to `README.md`. Also includes fixes for upstream issues [#116](https://github.com/custom-components/readme/issues/116) (`hass.components` removal) and [#104](https://github.com/custom-components/readme/issues/104) (Supervisor addons API deprecation).

## How it works

```
<config>/templates/README.md.j2              ──▶  <config>/README.md
<config>/templates/docs/index.md.j2          ──▶  <config>/docs/index.md
<config>/templates/docs/platform/network.md.j2 ──▶ <config>/docs/platform/network.md
```

Source path's `.j2` suffix is stripped; everything else (directory structure, filename, extension) maps 1:1.

## Next steps

- [Installation](installation.md)
- [Usage](usage.md)
- [Differences from upstream `readme`](differences.md)
