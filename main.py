import pandas as pd
import json
from google_play_scraper import Sort, reviews
import time

# Fungsi untuk mengambil ulasan dan menyimpan dalam CSV dan JSON
def scrape_traveloka_reviews(num_reviews=100, categories=None):
    try:
        # Validasi jumlah ulasan
        if num_reviews < 1:
            raise ValueError("Jumlah ulasan harus lebih dari 0")
        
        print(f"Mengambil {num_reviews} ulasan...")

        # Mengambil ulasan dari aplikasi Traveloka
        result, _ = reviews(
            'com.traveloka.android',  # App ID Traveloka
            lang='id',               # Bahasa Indonesia
            country='id',            # Negara Indonesia
            sort=Sort.NEWEST,        # Urutkan dari yang terbaru
            count=num_reviews        # Jumlah ulasan yang diambil
        )

        # Mengubah hasil ke DataFrame
        reviews_df = pd.DataFrame(result)

        # Memilih kolom yang relevan
        reviews_df = reviews_df[['userName', 'content', 'score', 'at', 'replyContent']]

        # Mengganti nama kolom untuk kejelasan
        reviews_df.columns = ['Username', 'Ulasan', 'Skor', 'Tanggal', 'Balasan']

        # Menambahkan kolom Country
        reviews_df['Country'] = 'id'  # Negara diisi sesuai parameter country

        # Mengatur urutan kolom
        reviews_df = reviews_df[['Username', 'Ulasan', 'Skor', 'Tanggal', 'Country', 'Balasan']]

        # Mengonversi kolom Tanggal dari Timestamp ke string
        reviews_df['Tanggal'] = reviews_df['Tanggal'].astype(str)

        # Filter kolom berdasarkan kategori yang dipilih
        if categories:
            # valid_categories = ['Username', 'Ulasan', 'Skor', 'Tanggal', 'Country', 'Balasan']
            valid_categories = ['Username', 'Ulasan', 'Tanggal']
            selected_categories = [cat for cat in categories if cat in valid_categories]
            if selected_categories:
                reviews_df = reviews_df[selected_categories]
            else:
                print("Kategori tidak valid, menggunakan semua kolom")

        # Menyimpan ke file CSV
        csv_file = 'traveloka_reviews.csv'
        reviews_df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"Ulasan berhasil disimpan ke {csv_file}")

        # Menyimpan ke file JSON dengan format pretty-printed
        json_file = 'traveloka_reviews.json'
        json_data = reviews_df.to_dict(orient='records')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        print(f"Ulasan berhasil disimpan ke {json_file}")

        print(f"Total ulasan yang diambil: {len(reviews_df)}")

        return reviews_df

    except Exception as e:
        print(f"Terjadi kesalahan: {str(e)}")
        return None

# Menjalankan fungsi
if __name__ == "__main__":
    start_time = time.time()
    num_reviews = 500  # Ubah ke 100, 300, atau 500 sesuai kebutuhan
    
    # Contoh penggunaan dengan kategori tertentu
    # Pilih kategori yang diinginkan: 'Username', 'Ulasan', 'Tanggal'
    # Kosongkan atau berikan None untuk mengambil semua kategori
    categories = ['Username', 'Ulasan', 'Tanggal']  # Ganti None untuk mengambil semua kategori
    
    scrape_traveloka_reviews(num_reviews=num_reviews, categories=categories)
    print(f"Waktu eksekusi: {time.time() - start_time} detik")