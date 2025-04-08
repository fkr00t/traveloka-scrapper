# Traveloka Reviews Scraper

Alat untuk mengambil ulasan aplikasi Traveloka dari Google Play Store dengan implementasi batasan permintaan untuk menghindari pemblokiran IP.

## Fitur

- Pengambilan review Traveloka dari Google Play Store
- Dukungan untuk pengurutan berdasarkan terbaru atau peringkat
- Penyimpanan hasil dalam format JSON dan CSV
- Implementasi delay acak untuk menghindari pembatasan rate
- Dua mode: pengambilan sederhana dan pengambilan data besar
- Logging untuk memantau proses pengambilan data

## Persyaratan

- Python 3.7+
- Paket yang diperlukan:
  - google-play-scraper
  - pandas
  - argparse
  - logging

## Instalasi

1. Clone repositori ini
2. Install dependensi yang diperlukan:

```
pip install -r requirements.txt
```

## Penggunaan

### Mode Pengambilan Sederhana

Gunakan mode simple untuk mengambil sejumlah kecil review dalam satu operasi:

```
python traveloka_reviews_scraper.py --mode simple --count 100 --sort newest
```

### Mode Pengambilan Data Besar

Gunakan mode large untuk mengambil data dalam jumlah besar:

```
python traveloka_reviews_scraper.py --mode large --count 5000 --batch 20 --delay-min 3 --delay-max 7 --output traveloka_data
```

### Parameter Command Line

| Parameter    | Deskripsi                                        | Default          |
|--------------|--------------------------------------------------|------------------|
| --mode       | Mode scraping (simple/large)                     | simple           |
| --count      | Jumlah review yang akan diambil                  | 100              |
| --batch      | Jumlah review per request                        | 20               |
| --sort       | Urutan review (newest/rating)                    | newest           |
| --lang       | Kode bahasa                                      | id               |
| --country    | Kode negara                                      | id               |
| --delay-min  | Delay minimum antar request (detik)              | 2.0              |
| --delay-max  | Delay maksimum antar request (detik)             | 5.0              |
| --output     | Direktori output (mode large)                    | traveloka_data   |
| --interval   | Dipertahankan untuk kompatibilitas (tidak digunakan) | 500              |
| --merge      | Dipertahankan untuk kompatibilitas (tidak digunakan) | False            |

## Output

### Mode Simple
- Menghasilkan dua file:
  - `traveloka_reviews_TIMESTAMP.json`: Data lengkap dalam format JSON
  - `traveloka_reviews_TIMESTAMP.csv`: Data dalam format CSV

### Mode Large
- Menghasilkan dua file (tanpa pemisahan part):
  - `traveloka_reviews_TIMESTAMP.json`: Data lengkap dalam format JSON
  - `traveloka_reviews_TIMESTAMP.csv`: Data dalam format CSV

## Contoh Output

Format JSON:
```json
[
  {
    "reviewId": "gp:AOqpTOFavGqgOmKcGTZ-jlsG38Hqr4...",
    "userName": "John Doe",
    "userImage": "https://play-lh.googleusercontent.com/a/...",
    "content": "Aplikasi sangat bagus dan mudah digunakan...",
    "score": 5,
    "thumbsUpCount": 0,
    "reviewCreatedVersion": "3.44.0",
    "at": "2023-04-12 09:42:38",
    "replyContent": "Halo John, Terima kasih atas ulasannya...",
    "repliedAt": "2023-04-12 13:10:05"
  },
  ...
]
```

Format CSV:
```
reviewId,userName,userImage,content,score,thumbsUpCount,reviewCreatedVersion,at,replyContent,repliedAt
gp:AOqpTOFavGqgOmKcGTZ-jlsG38Hqr4...,John Doe,https://play-lh.googleusercontent.com/a/...,Aplikasi sangat bagus dan mudah digunakan...,5,0,3.44.0,2023-04-12 09:42:38,Halo John Terima kasih atas ulasannya...,2023-04-12 13:10:05
...
```

## Peringatan

- Google Play Store memiliki mekanisme anti-bot dan bisa memblokir permintaan berlebihan
- Selalu gunakan ukuran batch yang kecil dan delay yang cukup untuk menghindari pemblokiran
- Disarankan untuk menggunakan mode large dengan batch kecil (10-20) dan delay yang lebih lama (3-7 detik)
- Gunakan dengan bijak dan bertanggung jawab

## Lisensi

MIT License

## Kontribusi

Kontribusi dan saran sangat dihargai! Silakan buat issue atau pull request jika Anda memiliki ide untuk perbaikan. 