"""학습·검증: 과거 연도로 학습, 최근 연도로 검증.

랜덤 분리를 쓰지 않는 이유
- 방문객 수는 시계열 특성이 있어 랜덤 분리 시 미래 정보가 학습에 섞인다(데이터 누수)
- 실제 사용 환경도 '과거 데이터로 미래 예측'이므로 검증도 같은 조건이어야 한다
"""

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

BASE_FEATURES = ["temp_c", "humidity_pct", "wind_ms"]
NEW_FEATURES = BASE_FEATURES + ["apparent_temp"]


def split_by_year(df: pd.DataFrame):
    last_year = df["year"].max()
    train = df[df["year"] < last_year]
    valid = df[df["year"] == last_year]
    return train, valid, last_year


def fit_and_score(train, valid, features):
    model = LinearRegression()
    model.fit(train[features], train["visitors"])
    pred = model.predict(valid[features])
    return r2_score(valid["visitors"], pred)


if __name__ == "__main__":
    df = pd.read_csv("data/processed/festival_features.csv").dropna()
    train, valid, last_year = split_by_year(df)
    print(f"학습: ~{last_year - 1}년 ({len(train)}행) / 검증: {last_year}년 ({len(valid)}행)\n")

    r2_base = fit_and_score(train, valid, BASE_FEATURES)
    r2_new = fit_and_score(train, valid, NEW_FEATURES)

    print(f"R² (기온·습도·풍속)      : {r2_base:.2f}")
    print(f"R² (+ 체감기온 파생변수) : {r2_new:.2f}")
    print(f"개선 폭                  : +{r2_new - r2_base:.2f}")
