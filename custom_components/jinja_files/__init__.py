"""
jinja_files — render every *.j2 file under <config>/templates/ to its
corresponding relative location.

Source path mapping:
    <config>/templates/foo/bar.md.j2  ->  <config>/foo/bar.md

Forked from custom-components/readme; generalized and patched for
upstream issues #116 (hass.components removal) and #104
(supervisor_info addons deprecation).
"""

from __future__ import annotations

import asyncio
import fnmatch
import os
from pathlib import Path
from typing import Any, Dict, List

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.template import AllStates
from homeassistant.loader import (
    Integration,
    IntegrationNotFound,
    async_get_integration,
)
from homeassistant.setup import async_get_loaded_integrations
from jinja2 import Template, TemplateError

# Per custom-components/readme issue #104, the recommended modern API
# for installed add-ons is `homeassistant.components.hassio.get_addons_info`,
# which returns a {slug: info} dict.
#
# NOTE: `is_hassio` is NOT exported from `homeassistant.components.hassio`
# in the 2026.5.x stable release (or in dev). We do the equivalent check
# inline with `"hassio" in hass.config.components`.
try:
    from homeassistant.components.hassio import get_addons_info
except ImportError:  # pragma: no cover — Core-only / non-Supervisor installs
    get_addons_info = None  # type: ignore[assignment]

from .const import (
    DOMAIN,
    LOGGER,
    STARTUP_MESSAGE,
    TEMPLATE_SUFFIX,
    TEMPLATES_DIR_NAME,
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({})},
    extra=vol.ALLOW_EXTRA,
)

RENDER_SCHEMA = vol.Schema(
    {
        vol.Optional("path"): cv.string,
        vol.Optional("override", default=False): cv.boolean,
    }
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """YAML-style setup (legacy)."""
    if config.get(DOMAIN) is None:
        return True
    LOGGER.info(STARTUP_MESSAGE)
    hass.data.setdefault(DOMAIN, {})
    await _async_register_services(hass)
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data={},
        )
    )
    return True


async def async_setup_entry(
    hass: HomeAssistant, config_entry: config_entries.ConfigEntry
) -> bool:
    """Config-entry setup (UI / config-flow)."""
    if config_entry.source == config_entries.SOURCE_IMPORT:
        # Avoid registering twice when the YAML path also created an entry.
        if hass.data.get(DOMAIN) is None:
            hass.async_create_task(
                hass.config_entries.async_remove(config_entry.entry_id)
            )
        return True

    LOGGER.info(STARTUP_MESSAGE)
    hass.data.setdefault(DOMAIN, {})
    await _async_register_services(hass)
    return True


async def async_unload_entry(
    hass: HomeAssistant, config_entry: config_entries.ConfigEntry
) -> bool:
    """Unload the entry so it can be reloaded/removed without a restart."""
    if config_entry.source == config_entries.SOURCE_IMPORT:
        # The imported entry owns nothing — `async_setup_entry` returned
        # early and the service belongs to the YAML `async_setup` path.
        return True

    if hass.services.has_service(DOMAIN, "render"):
        hass.services.async_remove(DOMAIN, "render")
    hass.data.pop(DOMAIN, None)
    return True


async def async_remove_entry(
    hass: HomeAssistant, config_entry: config_entries.ConfigEntry
) -> None:
    """Tear down."""
    if hass.services.has_service(DOMAIN, "render"):
        hass.services.async_remove(DOMAIN, "render")
    hass.data.pop(DOMAIN, None)


async def _async_register_services(hass: HomeAssistant) -> None:
    """Register the `jinja_files.render` service (idempotent)."""
    if hass.services.has_service(DOMAIN, "render"):
        return

    async def service_render(call: ServiceCall) -> None:
        path = call.data.get("path")
        override = call.data.get("override", False)
        try:
            await render_all(hass, only=path, override=override)
        except Exception:  # noqa: BLE001 — log everything so the user sees it
            LOGGER.exception("jinja_files.render failed")

    hass.services.async_register(
        DOMAIN, "render", service_render, schema=RENDER_SCHEMA
    )


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


async def render_all(
    hass: HomeAssistant, only: str | None = None, override: bool = False
) -> None:
    """Render every `.j2` under `templates/`.

    If `only` is given it is matched against each template's path relative to
    `templates/` as a wildcard pattern (`*`, `?`, `[...]`). A plain path with
    no wildcards still matches that single file, e.g. `docs/index.md.j2`.

    If `override` is `False`, templates whose output file already exists are
    skipped instead of being overwritten.
    """
    templates_dir = Path(hass.config.path(TEMPLATES_DIR_NAME))
    if not templates_dir.is_dir():
        LOGGER.warning(
            "%s/ does not exist under the config directory; nothing to render",
            TEMPLATES_DIR_NAME,
        )
        return

    def _discover() -> list[Path]:
        return sorted(templates_dir.rglob(f"*{TEMPLATE_SUFFIX}"))

    files = await hass.async_add_executor_job(_discover)

    if only:
        files = [
            f
            for f in files
            if fnmatch.fnmatchcase(
                f.relative_to(templates_dir).as_posix(), only
            )
        ]
        if not files:
            LOGGER.error(
                "No template matching %s found under %s/",
                only,
                TEMPLATES_DIR_NAME,
            )
            return

    if not files:
        LOGGER.info("No .j2 templates found under %s/", TEMPLATES_DIR_NAME)
        return

    # Collect template variables ONCE — same context for every file in a run.
    custom_components = await _get_custom_integrations(hass)
    hacs_components = _get_hacs_components(hass)
    installed_addons = _get_installed_addons(hass)

    variables: Dict[str, Any] = {
        "custom_components": custom_components,
        "states": AllStates(hass),
        "hacs_components": hacs_components,
        "addons": installed_addons,
    }

    config_dir = Path(hass.config.path()).resolve()
    rendered = 0
    failed = 0
    skipped = 0

    for src in files:
        rel = src.relative_to(templates_dir)
        # Strip the .j2 suffix from the filename, keep the rest.
        dest_rel = rel.with_name(rel.name[: -len(TEMPLATE_SUFFIX)])
        dest = (config_dir / dest_rel).resolve()

        # Path-traversal guard: refuse to write outside the config dir.
        try:
            dest.relative_to(config_dir)
        except ValueError:
            LOGGER.error(
                "Refusing to write outside config dir: %s -> %s", rel, dest
            )
            failed += 1
            continue

        if not override and dest.exists():
            LOGGER.info("skipped %s -> %s (already exists)", rel, dest_rel)
            skipped += 1
            continue

        try:
            await hass.async_add_executor_job(
                _render_one, src, dest, variables
            )
        except TemplateError as exc:
            LOGGER.error("Template error in %s: %s", rel, exc)
            failed += 1
            continue
        except Exception:  # noqa: BLE001
            LOGGER.exception("Failed to render %s", rel)
            failed += 1
            continue

        LOGGER.info("rendered %s -> %s", rel, dest_rel)
        rendered += 1

    LOGGER.info(
        "jinja_files: %d rendered, %d skipped, %d failed, %d total",
        rendered,
        skipped,
        failed,
        len(files),
    )


def _render_one(src: Path, dest: Path, variables: Dict[str, Any]) -> None:
    """Read, render, and write a single template. Runs in the executor."""
    content = src.read_text(encoding="utf-8")
    template = Template(content)
    rendered = template.render(variables)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(rendered, encoding="utf-8")


# ---------------------------------------------------------------------------
# Context providers (ported from custom-components/readme, patched)
# ---------------------------------------------------------------------------


@callback
def _get_installed_addons(hass: HomeAssistant) -> List[Dict[str, Any]]:
    """Return installed Supervisor add-ons via `get_addons_info`.

    Per custom-components/readme issue #104.
    """
    if get_addons_info is None:
        return []
    if "hassio" not in hass.config.components:
        return []
    try:
        addons_info = get_addons_info(hass)
    except Exception:  # noqa: BLE001 — Supervisor not ready / API drift
        return []
    if not addons_info:
        return []
    return [info for info in addons_info.values() if info is not None]


def _get_hacs_components(hass: HomeAssistant) -> List[Dict[str, Any]]:
    """Return HACS-downloaded repositories (empty if HACS isn't loaded)."""
    hacs = hass.data.get("hacs")
    if hacs is None:
        return []
    repositories = getattr(hacs, "repositories", None)
    if repositories is None:
        return []
    downloaded = getattr(repositories, "list_downloaded", None) or []
    out: List[Dict[str, Any]] = []
    for repo in downloaded:
        data = repo.data.to_json() if hasattr(repo.data, "to_json") else {}
        out.append(
            {
                **data,
                "name": _hacs_repository_name(repo),
                "documentation": f"https://github.com/{repo.data.full_name}",
            }
        )
    return out


def _hacs_repository_name(repository) -> str:
    """Pretty-print a HACS repository's name."""
    name = None
    manifest = getattr(repository, "repository_manifest", None)
    if manifest is not None and getattr(manifest, "name", None):
        name = manifest.name
    if name is None:
        name = repository.data.full_name.split("/")[-1]
    name = name.replace("-", " ").replace("_", " ").strip()
    return name if name.isupper() else name.title()


async def _get_custom_integrations(hass: HomeAssistant) -> List[Dict[str, Any]]:
    """Return loaded non-builtin integrations."""
    results: List[Integration | IntegrationNotFound | BaseException] = (
        await asyncio.gather(
            *[
                async_get_integration(hass, domain)
                for domain in async_get_loaded_integrations(hass)
            ],
            return_exceptions=True,
        )
    )

    custom: List[Dict[str, Any]] = []
    for integration in results:
        if isinstance(integration, IntegrationNotFound):
            continue
        if isinstance(integration, BaseException):
            LOGGER.debug("Skipping integration lookup error: %r", integration)
            continue
        if integration.disabled or integration.is_built_in:
            continue
        custom.append(
            {
                "domain": integration.domain,
                "name": integration.name,
                "documentation": integration.documentation,
                "version": integration.version,
                "codeowners": integration.manifest.get("codeowners"),
            }
        )
    return custom
