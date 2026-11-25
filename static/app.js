const $ = id => document.getElementById(id);
const sliders = ["hujan", "seed"];
let fase = 0, daftarFase = [], dataBulan = [], timer = null, tunda = null, versi = 0, depan = "A";

function query() {
  return "fase=" + fase + "&" + sliders.map(s => s + "=" + $(s).value).join("&");
}

function tampilGambar(url, v) {
  // crossfade: muat ke gambar belakang, lalu tukar
  const belakang = $(depan === "A" ? "gambarB" : "gambarA"), muka = $(depan === "A" ? "gambarA" : "gambarB");
  belakang.onload = () => {
    if (v !== versi) return;
    belakang.style.opacity = 1; muka.style.opacity = 0; depan = depan === "A" ? "B" : "A";
    $("status").textContent = "";
  };
  belakang.onerror = () => { if (v === versi) $("status").textContent = "Gagal merender gambar."; };
  belakang.src = url;
}

function perbarui() {
  sliders.forEach(s => $("v_" + s).textContent = $(s).value);
  const q = query(), v = ++versi;
  $("status").textContent = "Merender...";
  tampilGambar("/render.png?" + q + "&t=" + Date.now(), v);
  document.querySelectorAll(".chip").forEach((c, i) => c.classList.toggle("on", i === fase));
  fetch("/api/info?" + q).then(r => r.json()).then(d => {
    if (v !== versi) return;
    const k = d.kondisi;
    $("badge").textContent = "Fase " + (k.fase + 1) + ": " + k.nama + " (" + k.hari + ")";
    $("o_indeks").textContent = k.indeks_kondisi + "/100";
    $("o_daun").textContent = k.jumlah_daun;
    $("o_mutu").textContent = k.mutu;
    $("o_ciri").textContent = k.ciri;
    $("o_catatan").innerHTML = "";
    k.catatan.forEach(c => { const li = document.createElement("li"); li.textContent = c; $("o_catatan").appendChild(li); });
    $("o_node").textContent = "Jumlah node: " + d.jumlah_node;
    $("o_tree").textContent = tulisPohon(d.scene_graph, 0);
  }).catch(() => {});
  $("prev").disabled = fase <= 0;
  $("next").disabled = fase >= daftarFase.length - 1;
}

function tulisPohon(n, lv) {
  let s = "  ".repeat(lv) + n.nama + (n.kali > 1 ? " x" + n.kali : "") + "\n";
  (n.anak || []).forEach(c => s += tulisPohon(c, lv + 1));
  return s;
}

function setFase(i) {
  fase = Math.max(0, Math.min(daftarFase.length - 1, i));
  perbarui();
}
function jadwal() { clearTimeout(tunda); tunda = setTimeout(perbarui, 120); }
sliders.forEach(s => $(s).addEventListener("input", jadwal));
$("prev").onclick = () => { stop(); setFase(fase - 1); };
$("next").onclick = () => { stop(); setFase(fase + 1); };

function stop() { if (timer) { clearInterval(timer); timer = null; $("play").innerHTML = "&#9654; Putar semua fase"; } }
$("play").onclick = () => {
  if (timer) { stop(); return; }
  if (fase >= daftarFase.length - 1) setFase(0);
  $("play").innerHTML = "&#9208; Jeda";
  timer = setInterval(() => {
    if (fase >= daftarFase.length - 1) { stop(); return; }
    setFase(fase + 1);
  }, 2200);
};

function isiPilihan(id, nilai) {
  const sel = $(id), lama = sel.value;
  [...sel.querySelectorAll("option:not([value=''])")].forEach(o => o.remove());
  nilai.forEach(v => { const o = document.createElement("option"); o.value = o.textContent = v; sel.appendChild(o); });
  if (nilai.includes(lama)) sel.value = lama;
}
function unik(arr) { return [...new Set(arr)]; }

function terapkanData() {
  const t = $("tahun").value, k = $("kecamatan").value, b = $("bulan").value;
  const d = dataBulan.find(r => r.tahun === t && r.wilayah === k && r.bulan === b);
  if (!d) { $("ketdata").textContent = "Pilih bulan untuk memakai data BPS, atau atur slider secara manual."; return; }
  $("hujan").value = Math.round(Number(d.curah_hujan_mm) / 5) * 5;
  $("ketdata").textContent = d.bulan + " " + d.tahun + ", Kec. " + d.wilayah + ": " + d.curah_hujan_mm +
    " mm (rata-rata " + d.jumlah_stasiun + " stasiun). Status: " + d.status_data + ". " + d.sumber;
  perbarui();
}
$("tahun").addEventListener("change", () => {
  isiPilihan("kecamatan", unik(dataBulan.filter(r => r.tahun === $("tahun").value).map(r => r.wilayah)));
  terapkanData();
});
["kecamatan", "bulan"].forEach(id => $(id).addEventListener("change", terapkanData));
$("hujan").addEventListener("input", () => { $("bulan").value = ""; $("ketdata").textContent = "Mode manual."; });

(async function init() {
  const [f, d] = await Promise.all([fetch("/api/fase").then(r => r.json()), fetch("/api/data").then(r => r.json())]);
  daftarFase = f; dataBulan = d;
  f.forEach((x, i) => {
    const b = document.createElement("button");
    b.className = "chip"; b.innerHTML = "<b>" + x.no + "</b><br>" + x.nama;
    b.onclick = () => { stop(); setFase(i); };
    $("chips").appendChild(b);
  });
  const tahun = unik(d.map(r => r.tahun)).sort().reverse();
  isiPilihan("tahun", tahun);
  isiPilihan("kecamatan", unik(d.filter(r => r.tahun === tahun[0]).map(r => r.wilayah)));
  isiPilihan("bulan", unik(d.map(r => r.bulan)));
  terapkanData();
  perbarui();
})();
