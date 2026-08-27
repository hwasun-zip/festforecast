"""학습·검증: 과거 연도로 학습, 최근 연도로 검증.

핵심 피처는 '과거 방문 이력'(같은 축제의 이전 연도 방문객, log 스케일)이다.
방문객 수는 축제 규모에 따라 스케일 차이가 커서 log 변환한 값을 예측 대상으로 쓴다.

랜덤 분리를 쓰지 않는 이유
- 방문객 수는 시계열 특성이 있어 랜덤 분리 시 미래 정보가 학습에 섞인다(데이터 누수)
- 실제 사용 환경도 '과거 데이터로 미래 예측'이므로 검증도 같은 조건이어야 한다
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

WEATHER_FEATURES = ["temp_c", "humidity_pct", "wind_ms"]
WEATHER_PLUS_APPARENT = WEATHER_FEATURES + ["apparent_temp"]


def add_history_feature(df: pd.DataFrame) -> pd.DataFrame:
    """같은 축제(festival_name+region)의 이전 연도 log방문객 평균을 'history' 피처로 붙인다."""
    df = df.copy()
    df["log_visitors"] = np.log10(df["visitors"].clip(lower=1))
    df["key"] = df["region"] + "|" + df["festival_name"]

    history_values = []
    for _, row in df.iterrows():
        past = df[(df["key"] == row["key"]) & (df["year"] < row["year"])]
        history_values.append(past["log_visitors"].mean() if len(past) else np.nan)
    df["history"] = history_values
    return df


def split_by_year(df: pd.DataFrame):
    last_year = df["year"].max()
    train = df[df["year"] < last_year]
    valid = df[df["year"] == last_year]
    return train, valid, last_year


def fit_and_score(train, valid, features):
    train = train.dropna(subset=features + ["log_visitors"])
    valid = valid.dropna(subset=features + ["log_visitors"])
    if len(train) == 0 or len(valid) == 0:
        return float("nan")
    model = LinearRegression()
    model.fit(train[features], train["log_visitors"])
    pred = model.predict(valid[features])
    return r2_score(valid["log_visitors"], pred)


if __name__ == "__main__":
    df = pd.read_csv("data/processed/festival_features.csv")
    df = add_history_feature(df)
    train, valid, last_year = split_by_year(df)
    print(f"학습: ~{last_year - 1}년 ({len(train)}행) / 검증: {last_year}년 ({len(valid)}행)\n")

    r2_history_only = fit_and_score(train, valid, ["history"])
    r2_history_weather = fit_and_score(train, valid, ["history"] + WEATHER_FEATURES)
    r2_history_apparent = fit_and_score(train, valid, ["history"] + WEATHER_PLUS_APPARENT)

    print(f"R² (과거 방문 이력만)      : {r2_history_only:.3f}")
    print(f"R² (+ 기온, 습도, 풍속)    : {r2_history_weather:.3f}")
    print(f"R² (+ 체감기온 파생변수)   : {r2_history_apparent:.3f}")
