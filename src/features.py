"""파생변수: 체감기온.

배경
- 기온·강수량·요일 변수로는 R²가 0.70에서 정체
- EDA에서 같은 기온인데 방문객이 크게 갈리는 날들을 발견 -> 습도·풍속이 달랐다
- 가설: 사람은 측정 기온이 아니라 몸으로 느끼는 날씨에 반응한다

체감기온 근사식 (Steadman apparent temperature, 호주 기상청 방식)
    AT = T + 0.33e - 0.70ws - 4.0
    e(수증기압) = (습도/100) x 6.105 x exp(17.27T / (237.7 + T))
"""

import numpy as np
import pandas as pd


def apparent_temperature(temp_c, humidity_pct, wind_ms):
    e = (humidity_pct / 100.0) * 6.105 * np.exp(17.27 * temp_c / (237.7 + temp_c))
    return temp_c + 0.33 * e - 0.70 * wind_ms - 4.0


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["apparent_temp"] = apparent_temperature(
        df["temp_c"], df["humidity_pct"], df["wind_ms"]
    )
    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/festival_weather.csv")
    df = add_features(df)
    df.to_csv("data/processed/festival_features.csv", index=False)
    print("체감기온 변수 추가 완료")
    print(df[["temp_c", "humidity_pct", "wind_ms", "apparent_temp"]].describe())
