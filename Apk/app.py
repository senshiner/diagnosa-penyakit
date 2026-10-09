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
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* { box-sizing: border-box; }
body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0;
       background: #0f172a; color: #e2e8f0; }
.nav { background: #1e293b; padding: 14px 28px; display: flex;
       align-items: center; justify-content: space-between;
       position: sticky; top: 0; border-bottom: 2px solid #22d3ee; }
.nav .logo { font-size: 20px; font-weight: bold; color: #22d3ee; }
.nav .menu a { color: #cbd5e1; text-decoration: none; margin-left: 18px;
               font-size: 15px; }
.nav .menu a:hover, .nav .menu a.on { color: #22d3ee; font-weight: bold; }
.wrap { max-width: 860px; margin: 30px auto; padding: 0 18px; }
.hero { background: linear-gradient(135deg, #1e293b, #0e7490);
        border-radius: 16px; padding: 30px; margin-bottom: 22px;
        border: 1px solid #155e75; }
.hero h2 { margin: 0 0 8px 0; color: white; }
.hero p { margin: 0; color: #a5f3fc; }
.card { background: #1e293b; border: 1px solid #334155; border-radius: 14px;
        padding: 26px; margin-bottom: 18px; }
.card h2, .card h3 { color: #22d3ee; margin-top: 0; }
.tombol { display: inline-block; background: #22d3ee; color: #0f172a;
          padding: 12px 28px; border-radius: 10px; text-decoration: none;
          font-weight: bold; border: none; cursor: pointer; margin: 6px 6px 0 0; }
.tombol.ghost { background: transparent; color: #22d3ee;
                border: 1px solid #22d3ee; }
.gejala { column-count: 3; }
.gejala label { display: block; padding: 6px 8px; margin: 3px;
                background: #0f172a; border: 1px solid #334155;
                border-radius: 8px; font-size: 14px; cursor: pointer; }
.gejala label:hover { border-color: #22d3ee; }
input[type=text], input[type=number], select { padding: 11px; border-radius: 8px;
        border: 1px solid #475569; background: #0f172a; color: #e2e8f0;
        width: 100%; max-width: 340px; }
.hasil { border: 1px solid #22d3ee; background: #0c2b33; border-radius: 12px;
         padding: 20px; }
.footer { text-align: center; font-size: 12px; color: #64748b;
          margin: 26px 0 40px 0; }
ul { line-height: 1.7; }
</style></head>
<body>
<div class="nav">
  <div class="logo">&#128138; Diagnosa Penyakit</div>
  <div class="menu">
    <a href="/" class="{{ m_home }}">Data Pasien</a>
    <a href="/forward" class="{{ m_fw }}">Forward</a>
    <a href="/backward" class="{{ m_bw }}">Backward</a>
  </div>
</div>
<div class="wrap">
  {{ hero|safe }}
  <div class="card">{{ isi|safe }}</div>
  <div class="footer">Untuk edukasi saja, bukan pengganti diagnosa medis.<br>
  Dataset: {{ n }} penyakit &middot; {{ m }} gejala</div>
</div>
</body></html>
"""


def render(isi, menu='', hero=''):
    cls = {'home': '', 'fw': '', 'bw': ''}
    if menu in cls:
        cls[menu] = 'on'
    return render_template_string(
        BASE, isi=isi, hero=hero, n=len(DISEASES), m=len(SYMPTOMS),
        m_home=cls['home'], m_fw=cls['fw'], m_bw=cls['bw'])

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        umur = request.form.get('umur', '').strip()
        jk = request.form.get('jk', '')
        if not nama or not umur or not jk:
            return render('<p>Nama, umur, dan jenis kelamin wajib diisi.</p>'
                          '<a class="tombol" href="/">Kembali</a>', menu='home')
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
    <button type="submit" class="tombol">Lanjut &#8594;</button>
    </form>
    """
    hero = ('<div class="hero"><h2>Selamat datang</h2>'
            '<p>Isi data pasien untuk memulai diagnosa penyakit.</p></div>')
    return render(isi, menu='home', hero=hero)

@app.route('/metode')
def metode():
    if 'pasien' not in session:
        return redirect(url_for('home'))
    p = session['pasien']
    isi = f"""
    <h2>Halo, {p['nama']}</h2>
    <p>Pilih metode diagnosa:</p>
    <a class="tombol" href="/forward">Forward Chaining</a>
    <a class="tombol ghost" href="/backward">Backward Chaining</a>
    <h3>Tentang Dataset</h3>
    <p>Sumber: {SOURCE}. Berisi {len(DISEASES)} penyakit
    dan {len(SYMPTOMS)} gejala.</p>
    """
    hero = ('<div class="hero"><h2>Halo, {n}</h2>'
            '<p>Pilih metode diagnosa yang diinginkan.</p></div>').format(
                n=session['pasien']['nama'])
    return render(isi, menu='', hero=hero)

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
                          menu='fw')
        hasil = []
        for penyakit, daftar in DISEASES.items():
            cocok = dipilih & set(daftar)
            if cocok:
                hasil.append((len(cocok), penyakit, cocok))
        hasil.sort(reverse=True)
        if not hasil:
            return render('<p>Tidak ada penyakit yang cocok.</p>'
                          '<a class="tombol" href="/forward">Kembali</a>',
                          menu='fw')
        skor, penyakit, cocok = hasil[0]
        items = ''.join(f'<li>{tampil(g)}</li>' for g in sorted(cocok))
        isi = f"""
        <h2>Hasil Diagnosa</h2>
        <p>Pasien: <b>{pasien['nama']}</b> ({pasien['umur']} tahun,
           {pasien['jk']})</p>
        <p>Penyakit: <b>{penyakit}</b></p>
        <p>Gejala cocok: {skor}</p>
        <ul>{items}</ul>
        <p><i>Segera konsultasi ke dokter untuk kepastian.</i></p>
        <a class="tombol" href="/">Diagnosa ulang</a>
        """
        return render(isi, menu='fw')
    kotak = ''.join(
        f'<label><input type="checkbox" name="gejala" value="{g}">'
        f'{tampil(g)}</label><br>' for g in sorted(SYMPTOMS))
    isi = f"""
    <h2>Forward Chaining</h2>
    <p>Centang gejala yang dirasakan:</p>
    <input type="text" id="cari" placeholder="Cari gejala..."
           onkeyup="saring()" style="width:100%;padding:8px;margin-bottom:10px;">
    <form method="post"><div class="gejala" id="daftar">{kotak}</div>
    <br><button type="submit" class="tombol">Diagnosa</button></form>
    <a class="tombol ghost" href="/">Beranda</a>
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
    hero = ('<div class="hero"><h2>Forward Chaining</h2>'
            '<p>Centang semua gejala yang dirasakan pasien.</p></div>')
    return render(isi, menu='fw', hero=hero)

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
            isi = '<h2>Hasil</h2><p>Tidak ditemukan penyakit yang cocok.</p>'
        else:
            p = kandidat[0]
            items = ''.join(f'<li>{tampil(g)}</li>'
                            for g in sorted(DISEASES[p]))
            isi = (f'<h2>Hasil Diagnosa</h2>'
                   f'<p>Pasien: <b>{pasien["nama"]}</b></p>'
                   f'<p>Penyakit: <b>{p}</b></p>'
                   f'<p>Gejala penyakit ini:</p><ul>{items}</ul>'
                   f'<p><i>Segera konsultasi ke dokter untuk kepastian.</i></p>')
        return render(isi + '<a class="tombol" href="/">Diagnosa ulang</a>',
                      menu='bw')
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
                class="tombol">Ya</button>
        <button type="submit" name="jawab" value="tidak"
                class="tombol ghost">Tidak</button>
    </form>
    """
    return render(isi)

if __name__ == '__main__':
    app.run(debug=True)
