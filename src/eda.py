"""EDA: 성능 정체의 원인을 데이터에서 찾는다.

R²가 0.70에서 막혔을 때 모델을 바꾸는 대신 이 산점도를 다시 봤다.
같은 기온 구간에서 방문객이 2배 이상 갈리는 점들이 보였고,
그 점들을 나눠 보니 습도·풍속이 달랐다. -> features.py의 체감기온 가설로 연결
"""

import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


def scatter_temp_visitors(df: pd.DataFrame, out: str = "figures/temp_vs_visitors.png"):
    fig, ax = plt.subplots(figsize=(8, 5))
    sc = ax.scatter(df["temp_c"], df["visitors"], c=df["humidity_pct"], alpha=0.7)
    fig.colorbar(sc, label="습도(%)")
    ax.set_xlabel("평균기온(°C)")
    ax.set_ylabel("방문객 수")
    ax.set_title("기온 vs 방문객 - 색이 습도. 같은 기온에서 갈리는 점들을 볼 것")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"저장: {out}")


def outlier_days(df: pd.DataFrame, temp_band: float = 1.0) -> pd.DataFrame:
    """같은 기온대(±temp_band°C)에서 방문객 편차가 큰 날들을 추린다."""
    rows = []
    for t in range(int(df["temp_c"].min()), int(df["temp_c"].max()) + 1):
        band = df[(df["temp_c"] >= t - temp_band) & (df["temp_c"] <= t + temp_band)]
        if len(band) < 4:
            continue
        if band["visitors"].max() >= band["visitors"].min() * 2:
            rows.append(band.assign(temp_center=t))
    return pd.concat(rows).drop_duplicates() if rows else pd.DataFrame()


if __name__ == "__main__":
    df = pd.read_csv("data/processed/festival_weather.csv")
    scatter_temp_visitors(df)
    odd = outlier_days(df)
    if not odd.empty:
        print("\n같은 기온인데 방문객이 2배 이상 갈린 구간:")
        print(odd[["festival_name", "temp_c", "humidity_pct", "wind_ms", "visitors"]]
              .sort_values("temp_c").to_string(index=False))
