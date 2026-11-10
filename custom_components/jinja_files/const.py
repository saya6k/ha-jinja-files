"""Constants for the jinja_files integration."""

from __future__ import annotations

import logging

DOMAIN = "jinja_files"
LOGGER = logging.getLogger(__package__)

TEMPLATES_DIR_NAME = "templates"
TEMPLATE_SUFFIX = ".j2"

STARTUP_MESSAGE = (
    "----------------------------------------------------------------------\n"
    "  jinja_files — render every templates/*.j2 file into the config dir.\n"
    "  Service: jinja_files.render\n"
    "  Source: https://github.com/saya6k/ha-jinja-files\n"
    "----------------------------------------------------------------------"
)
