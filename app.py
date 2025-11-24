from flask import Flask, send_file, render_template_string
import io
import matplotlib
matplotlib.use("Agg")  # サーバー環境でも描画できるようにする
import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)

# ---------- トップページ（とりあえず動作確認用） ----------
@app.route("/")
def index():
    return "Sesoko tank data app is running."


# ---------- グラフページ（/sgr） ----------
@app.route("/sgr")
def sgr_page():
    """
    グラフを埋め込んだ簡単なHTMLを返す
    """
    html = """
    <html>
      <head>
        <meta charset="utf-8">
        <title>Sesoko Tank SGR</title>
      </head>
      <body>
        <h2>Sample SGR Graph (dummy)</h2>
        <img src="/sgr.png" alt="SGR graph">
      </body>
    </html>
    """
    return render_template_string(html)


# ---------- 実際の画像を返すエンドポイント ----------
@app.route("/sgr.png")
def sgr_png():
    """
    ダミーデータで折れ線グラフを描画してPNGとして返す。
    後でここを「NAICeのCSV → pandas → グラフ」に差し替える。
    """
    # いまはテストなのでダミーデータ
    x = np.arange(1, 13)  # 月（1〜12）
    y = np.linspace(0.5, 1.5, 12)  # 適当なS G R っぽい値

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, y, marker="o")
    ax.set_xlabel("Month")
    ax.set_ylabel("SGR (dummy)")
    ax.grid(True)

    # PNGとしてメモリに保存
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)

    return send_file(buf, mimetype="image/png")


if __name__ == "__main__":
    # ローカルテスト用
    app.run(debug=True)