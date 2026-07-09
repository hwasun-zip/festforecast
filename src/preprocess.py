"""전처리: 축제·날씨 데이터 표준화 및 결합.

이 프로젝트에서 가장 시간을 많이 쓴 구간.
- 축제마다 기간 표기가 달랐다: 일 단위(2024-03-25)와 월 단위(2024-03)가 섞여 있음
- 지역 표기도 제각각: "경남 진해" / "진해시" / "창원시 진해구"
- 해결: 날짜는 일 단위 기준으로 통일하되, 월까지만 있는 축제는
  해당 월의 날씨를 평균 내어 월 단위로 매칭
"""

import pandas as pd

FESTIVAL_RENAME = {
    "축제명": "festival_name",
    "개최지역": "region",
    "축제시작일자": "start_date",
    "축제종료일자": "end_date",
    "방문객수": "visitors",
}

WEATHER_RENAME = {
    "지점명": "region",
    "일시": "date",
    "평균기온(°C)": "temp_c",
    "평균상대습도(%)": "humidity_pct",
    "평균풍속(m/s)": "wind_ms",
}

# 지역 표기 통일: 내려받은 데이터를 보고 필요한 매핑을 추가한다
REGION_ALIAS = {
    "진해시": "경남 진해",
    "창원시 진해구": "경남 진해",
}


def load_festival(path: str) -> pd.DataFrame:
    df = pd.read_csv(path).rename(columns=FESTIVAL_RENAME)
    df["region"] = df["region"].str.strip().replace(REGION_ALIAS)

    # 월까지만 표기된 행 구분 (예: "2024-03" → 길이 7)
    df["month_only"] = df["start_date"].astype(str).str.len() <= 7

    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")
    df["year"] = df["start_date"].dt.year
    df["month"] = df["start_date"].dt.month
    return df.dropna(subset=["start_date", "visitors"])


def load_weather(path: str) -> pd.DataFrame:
    df = pd.read_csv(path).rename(columns=WEATHER_RENAME)
    df["region"] = df["region"].str.strip().replace(REGION_ALIAS)
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    return df


def attach_weather(fest: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    """축제 기간의 날씨를 붙인다.

    - 일 단위 축제: 개최 기간에 해당하는 날들의 날씨 평균
    - 월 단위 축제: 해당 월 전체의 날씨 평균 (일 매칭이 불가능하므로)
    """
    rows = []
    for _, f in fest.iterrows():
        w = weather[weather["region"] == f["region"]]
        if f["month_only"]:
            w = w[(w["year"] == f["year"]) & (w["month"] == f["month"])]
        else:
            w = w[(w["date"] >= f["start_date"]) & (w["date"] <= f["end_date"])]
        if w.empty:
            continue
        rows.append({
            "festival_name": f["festival_name"],
            "region": f["region"],
            "year": f["year"],
            "month": f["month"],
            "visitors": f["visitors"],
            "temp_c": w["temp_c"].mean(),
            "humidity_pct": w["humidity_pct"].mean(),
            "wind_ms": w["wind_ms"].mean(),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    fest = load_festival("data/raw/festival.csv")
    weather = load_weather("data/raw/weather.csv")
    merged = attach_weather(fest, weather)
    merged.to_csv("data/processed/festival_weather.csv", index=False)
    print(f"저장 완료: {len(merged)}행 -> data/processed/festival_weather.csv")
