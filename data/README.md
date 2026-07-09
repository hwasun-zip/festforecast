# 데이터 안내

원본 데이터는 용량·저작권 문제로 저장소에 포함하지 않습니다. 아래에서 직접 내려받아 `data/raw/`에 넣어주세요.

## 출처

| 파일 | 출처 | 내용 |
|---|---|---|
| `festival.csv` | 공공데이터포털 (data.go.kr) — "지역축제" 검색 | 지역 축제 개최 정보·방문객 수 (3개년) |
| `weather.csv` | 기상자료개방포털 (data.kma.go.kr) — 종관기상관측(ASOS) 일자료 | 일별 평균기온·습도·풍속 |

## 기대 스키마

`festival.csv`

| 컬럼 | 예시 |
|---|---|
| festival_name | ○○벚꽃축제 |
| region | 경남 진해 |
| start_date | 2024-03-25 (일부 행은 2024-03처럼 월까지만 존재) |
| end_date | 2024-04-05 |
| visitors | 152000 |

`weather.csv`

| 컬럼 | 예시 |
|---|---|
| region | 경남 진해 |
| date | 2024-03-25 |
| temp_c | 14.2 |
| humidity_pct | 62 |
| wind_ms | 2.1 |

실제 내려받은 파일의 컬럼명이 다르면 `src/preprocess.py` 상단의 `FESTIVAL_RENAME` / `WEATHER_RENAME` 딕셔너리만 수정하면 됩니다.
