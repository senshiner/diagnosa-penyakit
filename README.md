# Diagnosa Penyakit

Aplikasi web diagnosa penyakit berbasis dataset publik (Flask).

## Struktur

- `Apk/app.py` : aplikasi Flask (forward chaining + backward chaining)
- `Dataset/dataset.py` : dataset penyakit dan gejala (Python)

## Dataset

Dataset publik Disease Symptom Prediction (mirror GitHub dari dataset Kaggle):
66 penyakit dan 171 gejala. Untuk edukasi, bukan pengganti diagnosa medis.

## Cara menjalankan

```
pip install flask
cd Apk
python app.py
```

Buka http://127.0.0.1:5000
