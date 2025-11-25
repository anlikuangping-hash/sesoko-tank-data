from flask import Flask, send_file, render_template_string
import io
import datetime as dt

import matplotlib
matplotlib.use("Agg")  # サーバー環境で描画するおまじない
import matplotlib.pyplot as plt

import requests
import pandas as pd

app = Flask(__name__)


# ---------- トップページ ----------
@app.route("/")
def index():
    return "Sesoko tank data app is running.", 200


# ---------- グラフページ（HTML） ----------
@app.route("/sgr")
def sgr_page():
    """
    グラフを埋め込んだ簡単なHTMLを返す
    """
    html = """
    <html>
      <head>
        <meta charset="utf-8">
        <title>Sesoko Tank Data</title>
      </head>
      <body>
        <h2>Sesoko Tank SGR graph</h2>
        <p>もし画像が見えなければ /sgr.png に直接アクセスしてみてください。</p>
        <img src="/sgr.png" alt="SGR graph">
      </body>
    </html>
    """
    return render_template_string(html)


# ---------- グラフ画像（PNG） ----------
@app.route("/sgr.png")
def sgr_png():
    """
    - NAICe の CSV を取りに行く
    - 読み込めたらそのデータでグラフ
    - ダメだったらダミーデータでグラフ
    """

    # ==== 1) とりあえず「今日の日付のCSV」を取りに行く想定 ====
    # 例：2025-11-25 → 20251125.csv
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=9)))  # JST
    fname = today.strftime("%Y%m%d") + ".csv"
    base_url = "http://ik1-420-42083.vs.sakura.ne.jp/~isari/NAICe/"
    csv_url = base_url + fname

    use_dummy = False
    df = None

    try:
        res = requests.get(csv_url, timeout=5)
        if res.status_code == 200:
            # CSVをDataFrameに読み込み
            df = pd.read_csv(io.StringIO(res.text))
        else:
            use_dummy = True
    except Exception as e:
        print("CSV取得エラー:", e)
        use_dummy = True

    # ==== 2) グラフ描画 ====
    fig, ax = plt.subplots(figsize=(6, 4))

    if (df is not None) and (not use_dummy):
        try:
            # DATETIME を時刻に変換して TEMP をプロットする例
            # （本番では SGR 用の処理に差し替え）
            if "DATETIME" in df.columns and "TEMP" in df.columns:
                df["DATETIME"] = pd.to_datetime(df["DATETIME"])
                ax.plot(df["DATETIME"], df["TEMP"], marker="", linewidth=1)
                ax.set_xlabel("Time")
                ax.set_ylabel("Temperature (°C)")
                ax.set_title(fname)
            else:
                # 必要な列が無い場合はダミーにフォールバック
                use_dummy = True
        except Exception as e:
            print("グラフ描画中エラー:", e)
            use_dummy = True

    if use_dummy:
        # ダミーデータ（テスト用）
        import numpy as np
        x = np.arange(1, 13)
        y = np.linspace(0.5, 1.5, 12)
        ax.plot(x, y, marker="o")
        ax.set_xlabel("Month")
        ax.set_ylabel("SGR (dummy)")
        ax.set_title("Dummy SGR")

    ax.grid(True)

    # PNGとしてメモリに保存
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)

    return send_file(buf, mimetype="image/png")


if __name__ == "__main__":
    # ローカルテスト用（Renderでは gunicorn app:app が使われる）
    app.run(debug=True)
