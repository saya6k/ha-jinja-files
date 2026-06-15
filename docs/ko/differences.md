# upstream `readme`와의 차이점

| 항목 | `readme` | `jinja_files` |
| --- | --- | --- |
| 출력 | `templates/README.j2` → `README.md` 만 | `templates/` 아래의 모든 `*.j2` → `.j2`만 떼고 상대 경로 그대로 |
| 파일명 규칙 | 하드코드 | `.j2` 확장자만 제거 |
| 단일 파일 모드 | 없음 | `path:` 서비스 파라미터 |
| Supervisor API | `hass.components.hassio` (modern HA에서 깨짐) | `homeassistant.components.hassio.get_addons_info` |
| 애드온 목록 소스 | `supervisor_info.addons` (deprecated) | `get_addons_info(hass)` |
| Lovelace YAML 변환 | optional | 제거 (범위 외) |
