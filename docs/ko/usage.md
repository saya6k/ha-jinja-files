# 사용법

## 템플릿 컨텍스트

각 템플릿은 아래 변수들로 렌더링됩니다 (순수 Jinja2 — **`now()` 같은 HA 템플릿 헬퍼는 사용할 수 없고**, 아래 목록만 사용 가능):

| 변수 | 타입 | 설명 |
| --- | --- | --- |
| `states` | `AllStates` | HA 템플릿과 동일 — `states('sensor.foo')`, `states.sensor`, `states \| count` 등 |
| `addons` | `list[dict]` | 설치된 Supervisor 애드온. `name`, `slug`, `version`, `state`, `version_latest`, `update_available`, `repository`, `description` 등의 키 포함 |
| `hacs_components` | `list[dict]` | HACS로 다운로드된 저장소. `category` (`integration` / `plugin` / `theme` / …), `name`, `documentation`, `description`, `full_name` 등 |
| `custom_components` | `list[dict]` | 로드된 커스텀 통합. 키: `domain`, `name`, `documentation`, `version`, `codeowners` |

## 서비스

`templates/` 아래의 모든 `.j2` 파일 렌더링:

```yaml
service: jinja_files.render
```

단일 템플릿만 렌더링:

```yaml
service: jinja_files.render
data:
  path: docs/index.md.j2     # templates/ 기준 상대 경로
```

와일드카드(`*`, `?`, `[...]`)로 여러 템플릿 렌더링:

```yaml
service: jinja_files.render
data:
  path: docs/*.md.j2         # templates/docs/ 아래의 .md.j2 전부
```

### 기존 파일 덮어쓰기

기본적으로 서비스는 출력 파일이 이미 존재하면 해당 템플릿을 **건너뜁니다**. 따라서
다시 실행해도 직접 수정한 파일을 덮어쓰지 않습니다. 기존 출력을 덮어쓰려면
`override: true`를 전달하세요:

```yaml
service: jinja_files.render
data:
  override: true             # 이미 존재하는 출력 파일도 덮어씀
```
