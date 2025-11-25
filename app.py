import pandas as pd
from datetime import datetime, date
# すでに import があれば二重に書かなくてOK

BASE_URL = "http://ik1-420-42083.vs.sakura.ne.jp/~isari/NAICe"

def load_daily_data(target_date: date, tank="B1"):
    """
    指定した日付1日分のCSVを読み込んでDataFrameを返す関数
    target_date : datetime.date（例：date(2025, 11, 25)）
    tank        : "B1" / "B2" など。URLのパスに使う想定。
    """
    # 例：2025-11-25 → "20251125"
    datestr = target_date.strftime("%Y%m%d")

    # ☆ 実際のURLパターンに合わせてここを調整
    # 例：.../NAICe/B1/20251125.csv という構造を仮定
    csv_url = f"{BASE_URL}/{tank}/{datestr}.csv"

    # pandasはHTTPのCSVをそのまま読める
    df = pd.read_csv(csv_url)

    return df

def get_today_B1():
    today = datetime.now().date()
    df = load_daily_data(today, tank="B1")
    return df

@app.route("/debug_b1")
def debug_b1():
    today = datetime.now().date()
    df = load_daily_data(today, tank="B1")
    # 先頭5行だけテキストで返す
    return df.head().to_html()
