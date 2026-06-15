# Jinja Files

`<config>/templates/` 아래의 **모든 `.j2` 파일**을 대응 위치로 렌더링하는 Home Assistant 커스텀 통합. HA 상태, 설치된 애드온, HACS 컴포넌트를 템플릿 컨텍스트로 사용합니다.

[custom-components/readme](https://github.com/custom-components/readme) (Joakim Sørensen / @ludeeus)에서 fork — `README.md`에 국한되지 않도록 일반화했습니다. upstream 이슈 [#116](https://github.com/custom-components/readme/issues/116) (`hass.components` 제거)과 [#104](https://github.com/custom-components/readme/issues/104) (Supervisor addons API deprecation) 수정 포함.

## 동작 방식

```
<config>/templates/README.md.j2              ──▶  <config>/README.md
<config>/templates/docs/index.md.j2          ──▶  <config>/docs/index.md
<config>/templates/docs/platform/network.md.j2 ──▶ <config>/docs/platform/network.md
```

소스 경로의 `.j2` 접미사만 제거되고, 나머지(디렉터리 구조·파일명·확장자)는 1:1로 매핑됩니다.

## 다음 단계

- [설치](installation.md)
- [사용법](usage.md)
- [upstream `readme`와의 차이점](differences.md)
