"""Server Flask TembakauGacor: antarmuka web + gambar PNG dari Pycairo."""
import csv
import os

from flask import Flask, Response, jsonify, render_template, request

from graphics.growth import ASUMSI, FASE
from graphics.renderer import info_scene, render_png

app = Flask(__name__)
DATA_CSV = os.path.join(os.path.dirname(__file__), "data", "iklim_jember.csv")


def _angka(nama, default, lo, hi):
    """Ambil parameter query sebagai angka; nilai salah/NaN/di luar batas dibatasi, bukan error."""
    try:
        v = float(request.args.get(nama, default))
    except (TypeError, ValueError):
        v = default
    if v != v or v in (float("inf"), float("-inf")):
        v = default
    return max(lo, min(hi, v))


def _params():
    return (int(_angka("fase", 0, 0, len(FASE) - 1)), _angka("hujan", 100, 0, 1000),
            int(_angka("seed", 1, 0, 99999)))


def muat_data():
    with open(DATA_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@app.route("/")
def index():
    return render_template("index.html", asumsi=ASUMSI, jumlah_fase=len(FASE))


@app.route("/render.png")
def render():
    fase, hujan, seed = _params()
    return Response(render_png(fase, hujan, seed), mimetype="image/png",
                    headers={"Cache-Control": "no-store"})


@app.route("/api/info")
def info():
    fase, hujan, seed = _params()
    k, jumlah, pohon = info_scene(fase, hujan, seed)
    return jsonify({"kondisi": k, "jumlah_node": jumlah, "scene_graph": pohon})


@app.route("/api/fase")
def fase_list():
    return jsonify([{"no": i + 1, "nama": f["nama"], "hari": f["hari"], "ciri": f["ciri"]} for i, f in enumerate(FASE)])


@app.route("/api/data")
def data():
    return jsonify(muat_data())


if __name__ == "__main__":
    app.run(debug=True, port=5000)
