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
body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #e6f4f1;
       margin: 0; color: #1f2937; }
.header { background: linear-gradient(135deg, #0b6e64, #14b8a6);
          color: white; text-align: center; padding: 28px 20px;
          border-radius: 0 0 24px 24px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.header h1 { margin: 0 0 6px 0; letter-spacing: 1px; }
.box { background: white; width: 85%; max-width: 900px; margin: 24px auto;
       padding: 28px; border-radius: 16px;
       box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
a.btn, button.btn { display: inline-block; background: #0d9488; color: white;
        padding: 12px 26px; margin: 6px; text-decoration: none;
        border-radius: 999px; font-weight: bold; border: none;
        cursor: pointer; box-shadow: 0 2px 8px rgba(13,148,136,0.4); }
a.btn:hover, button.btn:hover { background: #0b7c72; }
.gejala { column-count: 3; }
.gejala label { display: block; padding: 4px 0; }
input[type=text], input[type=number], select {
        padding: 10px; border-radius: 8px; border: 1px solid #9fd8d0; }
.footer { background: #0b3f3a; color: #c8efe9; text-align: center;
          padding: 14px; font-size: 12px; margin-top: 30px; }
h2 { color: #0b6e64; }
</style></head>
<body>
<div class="header"><h1>Diagnosa Penyakit</h1>
<p>Basis data: {{ n }} penyakit, {{ m }} gejala (dataset publik)</p></div>
<div class="box">{{ isi|safe }}</div>
<div class="footer">Untuk edukasi saja, bukan pengganti diagnosa medis.</div>
</body></html>
"""

def render(isi):
    return render_template_string(BASE, isi=isi,
                                  n=len(DISEASES), m=len(SYMPTOMS))

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        umur = request.form.get('umur', '').strip()
        jk = request.form.get('jk', '')
        if not nama or not umur or not jk:
            return render('<p>Nama, umur, dan jenis kelamin wajib diisi.</p>'
                          '<a class="btn" href="/">Kembali</a>')
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
    <button type="submit" class="btn"
            style="border:none;cursor:pointer;">Lanjut</button>
    </form>
    """
    return render(isi)

@app.route('/metode')
def metode():
    if 'pasien' not in session:
        return redirect(url_for('home'))
    p = session['pasien']
    isi = f"""
    <h2>Halo, {p['nama']}</h2>
    <p>Pilih metode diagnosa:</p>
    <a class="btn" href="/forward">Forward Chaining (ceklist gejala)</a>
    <a class="btn" href="/backward">Backward Chaining (tanya jawab)</a>
    <h3>Tentang Dataset</h3>
    <p>Sumber: {SOURCE}. Berisi {len(DISEASES)} penyakit
    dan {len(SYMPTOMS)} gejala.</p>
    """
    return render(isi)

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
                          '<a class="btn" href="/forward">Kembali</a>')
        hasil = []
        for penyakit, daftar in DISEASES.items():
            cocok = dipilih & set(daftar)
            if cocok:
                hasil.append((len(cocok), penyakit, cocok))
        hasil.sort(reverse=True)
        if not hasil:
            return render('<p>Tidak ada penyakit yang cocok.</p>'
                          '<a class="btn" href="/forward">Kembali</a>')
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
        <a class="btn" href="/">Diagnosa ulang</a>
        """
        return render(isi)
    kotak = ''.join(
        f'<label><input type="checkbox" name="gejala" value="{g}">'
        f'{tampil(g)}</label><br>' for g in sorted(SYMPTOMS))
    isi = f"""
    <h2>Forward Chaining</h2>
    <p>Centang gejala yang dirasakan:</p>
    <input type="text" id="cari" placeholder="Cari gejala..."
           onkeyup="saring()" style="width:100%;padding:8px;margin-bottom:10px;">
    <form method="post"><div class="gejala" id="daftar">{kotak}</div>
    <br><button type="submit" class="btn"
            style="border:none;cursor:pointer;">Diagnosa</button></form>
    <a class="btn" href="/">Beranda</a>
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
    return render(isi)

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
        return render(isi + '<a class="btn" href="/">Diagnosa ulang</a>')
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
                class="btn" style="border:none;cursor:pointer;">Ya</button>
        <button type="submit" name="jawab" value="tidak"
                class="btn" style="border:none;cursor:pointer;">Tidak</button>
    </form>
    """
    return render(isi)

if __name__ == '__main__':
    app.run(debug=True)
