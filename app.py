from flask import Flask, send_file, render_template_string
import io
import os
import datetime

import requests
import pandas as pd

import matplotlib
matplotlib.use("Agg")  # サーバー環境でも描画できるようにする
import matplotlib.pyplot as plt

app = Flask(__name__)

# ==== NAICe データの設定 ==========================================
# ベースURL（必要に応じて変更）
BASE_URL = "http://ik1-420-42083.vs.sakura.ne.jp/~isari/NAICe"

# 今日の日付から CSV ファイル名を作る想定：YYYYMMDD.csv
def get_today_csv_url():
    today = datetime.date.today()
    filename = today.strftime("%Y%m%d") + ".csv"   # 例：20251125.csv
    return f"{BASE_URL}/{filename}"

def load_today_data():
    """
    今日の日付の CSV を NAICe から取得して DataFrame にして返す。
    DATETIME を datetime 型に変換する。
    """
    url = get_today_csv_url()
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        # 何かあれば例外を投げる → 呼び出し側で500を返す
        raise RuntimeError(f"CSV取得に失敗しました: {e}")

    # CSV を DataFrame に読み込む
    df = pd.read_csv(io.StringIO(r.text))

    # DATETIME 列を datetime 型に
    if "DATETIME" in df.columns:
        df["DATETIME"] = pd.to_datetime(df["DATETIME"])
    else:
        raise RuntimeError("CSV に DATETIME 列がありません")

    return df

# ==== ルーティング ===============================================

# トップページ（生存確認用）
@app.route("/")
def index():
    return "Sesoko tank data app is running.", 200


# グラフをまとめて表示するページ
# 例: https://sesoko-tank-data.onrender.com/sgr
@app.route("/sgr")
def sgr_page():
    """
    4つの環境項目（TEMP, DO, PH, SALT）のグラフ画像を
    <img> タグで並べて表示する簡単なページ。
    """
    html = """
    <html>
      <head>
        <meta charset="utf-8">
        <title>Sesoko Tank Data (Today)</title>
      </head>
      <body>
        <h2>Today's Tank Environment (Temp / DO / pH / Salinity)</h2>
        <div>
          <h3>Temperature</h3>
          <img src="/plot/temp" alt="Temperature">
        </div>
        <div>
          <h3>Dissolved Oxygen</h3>
          <img src="/plot/do" alt="DO">
        </div>
        <div>
          <h3>pH</h3>
          <img src="/plot/ph" alt="pH">
        </div>
        <div>
          <h3>Salinity</h3>
          <img src="/plot/salt" alt="Salinity">
        </div>
      </body>
    </html>
    """
    return render_template_string(html)


# 個別のグラフ画像を返すエンドポイント
@app.route("/plot/<kind>")
def plot_kind(kind):
    """
    /plot/temp  /plot/do  /plot/ph  /plot/salt
    のようにアクセスすると、その日の1日分の折れ線グラフPNGを返す。
    """
    # kind → CSV上の列名とラベルの対応
    col_map = {
        "temp": ("TEMP", "Temperature (°C)"),
        "do":   ("DO",   "Dissolved Oxygen (mg/L)"),
        "ph":   ("PH",   "pH"),
        "salt": ("SALT", "Salinity")
    }

    if kind not in col_map:
        return "Unknown plot type", 404

    column_name, ylabel = col_map[kind]

    try:
        df = load_today_data()
    except Exception as e:
        # ここでエラー内容を返しておく（必要ならログだけにしてもOK）
        return f"Error loading data: {e}", 500

    if column_name not in df.columns:
        return f"Column {column_name} not found in CSV", 500

    x = df["DATETIME"]
    y = df[column_name]

    # ==== グラフ作成 ====
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, y, marker=".", linewidth=1)

    ax.set_xlabel("Time")
    ax.set_ylabel(ylabel)
    ax.grid(True)

    # x軸のラベルを少し見やすく（自動調整）
    fig.autofmt_xdate()

    # PNGとしてメモリに保存
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)

    return send_file(buf, mimetype="image/png")


# ローカルテスト用
if __name__ == "__main__":
    # VSCode などで python app.py を実行したとき用
    # （Render では gunicorn app:app が使われる）
    app.run(debug=True)
