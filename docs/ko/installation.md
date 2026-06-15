# 설치

1. 이 repo를 HACS 커스텀 저장소(Integration 카테고리)로 추가합니다.
2. **Jinja Files**를 설치합니다.
3. Home Assistant를 재시작합니다.
4. `<config>/templates/` 아래에 `*.j2` 파일을 둡니다.
5. `jinja_files.render` 서비스를 호출합니다.

## 자동화 (예: 매일 밤)

```yaml
trigger:
  - platform: time
    at: '03:00:00'
action:
  - service: jinja_files.render
```
