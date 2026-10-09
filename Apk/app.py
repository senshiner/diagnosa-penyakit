"""Aplikasi diagnosa penyakit (forward chaining + backward chaining).

Dataset: Dataset/dataset.py (dataset publik Disease Symptom Prediction,
66 penyakit dan 171 gejala). Untuk edukasi, bukan pengganti diagnosa medis.
Jalankan: python app.py lalu buka http://127.0.0.1:5000
"""
from flask import Flask, request, render_template_string, redirect, url_for, session
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Dataset'))
from dataset import SYMPTOMS, DISEASES, tampil, SOURCE

app = Flask(__name__)
app.secret_key = 'diagnosa-penyakit'

BASE = """
<html><head><title>Diagnosa Penyakit</title>
<style>
* { box-sizing: border-box; }
body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0;
       background: #f7f5ef; color: #2d2a26; display: flex; }
.sidebar { width: 250px; min-height: 100vh; background: #1e3a2f; color: white;
           padding: 24px 18px; position: fixed; height: 100%; }
.sidebar .logo { font-size: 20px; font-weight: bold; margin-bottom: 6px;
                 color: #f5c518; }
.sidebar .sub { font-size: 12px; color: #b9d3cb; margin-bottom: 28px; }
.sidebar nav a { display: block; color: white; text-decoration: none;
                 padding: 12px 14px; margin: 6px 0; border-radius: 10px; }
.sidebar nav a:hover, .sidebar nav a.aktif { background: #f5c518; color: #1e3a2f;
                 font-weight: bold; }
.sidebar .info { margin-top: 30px; font-size: 12px; color: #b9d3cb;
                 border-top: 1px solid #3a5a4f; padding-top: 14px; }
.main { margin-left: 250px; flex: 1; padding: 28px 36px; }
.langkah { display: flex; gap: 8px; margin-bottom: 22px; }
.langkah span { background: #e2ddd0; padding: 8px 16px; border-radius: 999px;
                font-size: 13px; }
.langkah span.on { background: #1e3a2f; color: white; font-weight: bold; }
.kartu { background: white; border-radius: 14px; padding: 26px;
         border-left: 6px solid #f5c518;
         box-shadow: 0 2px 10px rgba(0,0,0,0.07); margin-bottom: 18px; }
.tombol { display: inline-block; background: #1e3a2f; color: white;
          padding: 12px 26px; border-radius: 10px; text-decoration: none;
          font-weight: bold; border: none; cursor: pointer; margin: 6px 4px 0 0; }
.tombol.kuning { background: #f5c518; color: #1e3a2f; }
.gejala { column-count: 3; }
.gejala label { display: block; padding: 5px 4px; background: #faf8f2;
                margin: 3px; border-radius: 6px; font-size: 14px; }
input[type=text], input[type=number], select { padding: 10px; border-radius: 8px;
        border: 1px solid #c9c2b2; width: 100%; max-width: 340px; }
.hasil-box { border: 2px dashed #1e3a2f; border-radius: 12px; padding: 20px;
             background: #fbfaf6; }
.footer { text-align: center; font-size: 12px; color: #8a8478; margin-top: 26px; }
h2 { margin-top: 0; color: #1e3a2f; }
</style></head>
<body>
<div class="sidebar">
  <div class="logo">Diagnosa Penyakit</div>
  <div class="sub">Sistem pakar berbasis dataset</div>
  <nav>
    <a href="/" class="{{ m_home }}">Data Pasien</a>
    <a href="/forward" class="{{ m_fw }}">Forward Chaining</a>
    <a href="/backward" class="{{ m_bw }}">Backward Chaining</a>
  </nav>
  <div class="info">Dataset publik<br>{{ n }} penyakit &middot; {{ m }} gejala</div>
</div>
<div class="main">
  <div class="langkah">{{ langkah|safe }}</div>
  <div class="kartu">{{ isi|safe }}</div>
  <div class="footer">Untuk edukasi saja, bukan pengganti diagnosa medis.</div>
</div>
</body></html>
"""


def render(isi, menu='', tahap=0):
    menu_cls = {'home': '', 'fw': '', 'bw': ''}
    if menu in menu_cls:
        menu_cls[menu] = 'aktif'
    nama_tahap = ['Data Pasien', 'Metode', 'Pemeriksaan', 'Hasil']
    langkah = ''.join(
        f'<span class="{"on" if i < tahap else ""}">{t}</span>'
        for i, t in enumerate(nama_tahap, 1))
    return render_template_string(
        BASE, isi=isi, langkah=langkah, n=len(DISEASES), m=len(SYMPTOMS),
        m_home=menu_cls['home'], m_fw=menu_cls['fw'], m_bw=menu_cls['bw'])

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        umur = request.form.get('umur', '').strip()
        jk = request.form.get('jk', '')
        if not nama or not umur or not jk:
            return render('<p>Nama, umur, dan jenis kelamin wajib diisi.</p>'
                          '<a class="tombol" href="/">Kembali</a>',
                        menu='home', tahap=1)
        session['pasien'] = {'nama': nama, 'umur': umur, 'jk': jk}
        return redirect(url_for('metode'))
    isi = """
    <h2>Data Pasien</h2>
    <form method="post">
    <p>Nama: <input type="text" name="nama" required></p>
    <p>Umur: <input type="number" name="umur" min="1" max="120" required></p>
    <p>Jenis kelamin:
      <select name="jk" required>
        <option value="">- pilih -</option>
        <option value="Laki-laki">Laki-laki</option>
        <option value="Perempuan">Perempuan</option>
      </select></p>
    <button type="submit" class="tombol kuning">Lanjut &#8594;</button>
    </form>
    """
    return render(isi, menu='home', tahap=1)

@app.route('/metode')
def metode():
    if 'pasien' not in session:
        return redirect(url_for('home'))
    p = session['pasien']
    isi = f"""
    <h2>Halo, {p['nama']}</h2>
    <p>Pilih metode diagnosa:</p>
    <div style="display:flex;gap:14px;flex-wrap:wrap;">
      <a class="tombol" href="/forward">&#128203; Forward Chaining<br>
        <small style="font-weight:normal">ceklist gejala</small></a>
      <a class="tombol kuning" href="/backward">&#10067; Backward Chaining<br>
        <small style="font-weight:normal">tanya jawab</small></a>
    </div>
    <h3>Tentang Dataset</h3>
    <p>Sumber: {SOURCE}. Berisi {len(DISEASES)} penyakit
    dan {len(SYMPTOMS)} gejala.</p>
    """
    return render(isi, menu='', tahap=2)

# ---------- Forward chaining: ceklist gejala ----------
@app.route('/forward', methods=['GET', 'POST'])
def forward():
    if 'pasien' not in session:
        return redirect(url_for('home'))
    pasien = session['pasien']
    if request.method == 'POST':
        dipilih = set(request.form.getlist('gejala'))
        if not dipilih:
            return render('<p>Pilih minimal satu gejala.</p>'
                          '<a class="tombol" href="/forward">Kembali</a>',
                          menu='fw', tahap=3)
        hasil = []
        for penyakit, daftar in DISEASES.items():
            cocok = dipilih & set(daftar)
            if cocok:
                hasil.append((len(cocok), penyakit, cocok))
        hasil.sort(reverse=True)
        if not hasil:
            return render('<p>Tidak ada penyakit yang cocok.</p>'
                          '<a class="tombol" href="/forward">Kembali</a>',
                          menu='fw', tahap=3)
        skor, penyakit, cocok = hasil[0]
        items = ''.join(f'<li>{tampil(g)}</li>' for g in sorted(cocok))
        isi = f"""
        <h2>Hasil Diagnosa</h2>
        <div class="hasil-box">
        <p>Pasien: <b>{pasien['nama']}</b> ({pasien['umur']} tahun,
           {pasien['jk']})</p>
        <p>Penyakit: <b>{penyakit}</b></p>
        <p>Gejala cocok: {skor}</p>
        <ul>{items}</ul>
        </div>
        <p><i>Segera konsultasi ke dokter untuk kepastian.</i></p>
        <a class="tombol kuning" href="/">Diagnosa ulang</a>
        """
        return render(isi, menu='fw', tahap=4)
    kotak = ''.join(
        f'<label><input type="checkbox" name="gejala" value="{g}">'
        f'{tampil(g)}</label><br>' for g in sorted(SYMPTOMS))
    isi = f"""
    <h2>Forward Chaining</h2>
    <p>Centang gejala yang dirasakan:</p>
    <input type="text" id="cari" placeholder="Cari gejala..."
           onkeyup="saring()" style="width:100%;padding:8px;margin-bottom:10px;">
    <form method="post"><div class="gejala" id="daftar">{kotak}</div>
    <br><button type="submit" class="tombol kuning">Diagnosa</button></form>
    <a class="tombol" href="/">Beranda</a>
    <script>
    function saring() {{
        var k = document.getElementById('cari').value.toLowerCase();
        var d = document.getElementById('daftar').getElementsByTagName('label');
        for (var i = 0; i < d.length; i++)
            d[i].style.display =
                d[i].textContent.toLowerCase().includes(k) ? '' : 'none';
    }}
    </script>
    """
    return render(isi, menu='fw', tahap=3)

# ---------- Backward chaining: tanya jawab ----------
def gejala_terbaik(kandidat):
    """Pilih gejala yang paling membelah kandidat jadi dua kelompok."""
    hitung = {}
    for p in kandidat:
        for g in DISEASES[p]:
            hitung[g] = hitung.get(g, 0) + 1
    n = len(kandidat)
    return min(hitung, key=lambda g: abs(hitung[g] - n / 2))

@app.route('/backward')
def backward():
    if 'pasien' not in session:
        return redirect(url_for('home'))
    session['kandidat'] = sorted(DISEASES)
    session['ditanya'] = []
    return redirect(url_for('tanya'))

@app.route('/tanya', methods=['GET', 'POST'])
def tanya():
    kandidat = session.get('kandidat', [])
    ditanya = session.get('ditanya', [])
    if request.method == 'POST':
        jawab = request.form.get('jawab')
        gejala = session.get('gejala_saat_ini')
        if jawab == 'ya':
            kandidat = [p for p in kandidat if gejala in DISEASES[p]]
        else:
            kandidat = [p for p in kandidat if gejala not in DISEASES[p]]
        session['kandidat'] = kandidat
    if len(kandidat) <= 1 or len(ditanya) >= 15:
        pasien = session.get('pasien', {'nama': '-', 'umur': '-', 'jk': '-'})
        if not kandidat:
            isi = ('<h2>Hasil</h2><div class="hasil-box">'
                   '<p>Tidak ditemukan penyakit yang cocok.</p></div>')
        else:
            p = kandidat[0]
            items = ''.join(f'<li>{tampil(g)}</li>'
                            for g in sorted(DISEASES[p]))
            isi = (f'<h2>Hasil Diagnosa</h2>'
                   f'<div class="hasil-box">'
                   f'<p>Pasien: <b>{pasien["nama"]}</b></p>'
                   f'<p>Penyakit: <b>{p}</b></p>'
                   f'<p>Gejala penyakit ini:</p><ul>{items}</ul>'
                   f'</div>'
                   f'<p><i>Segera konsultasi ke dokter untuk kepastian.</i></p>')
        return render(isi + '<a class="tombol kuning" href="/">Diagnosa ulang</a>',
                      menu='bw', tahap=4)
    gejala = gejala_terbaik(kandidat)
    # hindari tanya gejala yang sama dua kali
    if gejala in ditanya:
        for g in sorted(SYMPTOMS):
            if g not in ditanya:
                gejala = g
                break
    session['gejala_saat_ini'] = gejala
    if gejala not in ditanya:
        ditanya.append(gejala)
    session['ditanya'] = ditanya
    isi = f"""
    <h2>Backward Chaining</h2>
    <p>Pertanyaan {len(ditanya)} (kandidat tersisa: {len(kandidat)})</p>
    <h3>Apakah mengalami: {tampil(gejala)}?</h3>
    <form method="post">
        <button type="submit" name="jawab" value="ya"
                class="tombol kuning">Ya</button>
        <button type="submit" name="jawab" value="tidak"
                class="tombol">Tidak</button>
    </form>
    """
    return render(isi, menu='bw', tahap=3)

if __name__ == '__main__':
    app.run(debug=True)
