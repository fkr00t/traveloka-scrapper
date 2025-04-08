import time
import random
import json
import csv
import os
import argparse
import sys
from google_play_scraper import Sort, reviews
from datetime import datetime
import logging

# Menambahkan custom JSON encoder untuk menangani objek datetime
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)

class TravelokaReviewScraper:
    def __init__(self, lang='id', country='id'):
        """
        Inisialisasi scraper untuk review Traveloka
        
        Args:
            lang (str): Bahasa untuk review (default: 'id' untuk Bahasa Indonesia)
            country (str): Kode negara (default: 'id' untuk Indonesia)
        """
        self.app_id = 'com.traveloka.android'
        self.lang = lang
        self.country = country
        self.delay_min = 2  # Delay minimum dalam detik
        self.delay_max = 5  # Delay maksimum dalam detik
        
        # Konfigurasi logging
        logging.basicConfig(
            filename='traveloka_scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('TravelokaScraper')
        
    def _random_delay(self):
        """Menerapkan delay acak untuk menghindari pemblokiran"""
        delay = random.uniform(self.delay_min, self.delay_max)
        print(f"Menunggu {delay:.2f} detik...")
        time.sleep(delay)
    
    def scrape_reviews(self, count=100, sort=Sort.NEWEST, batch_size=20):
        """
        Mengambil review Traveloka dari Play Store
        
        Args:
            count (int): Jumlah review yang ingin diambil
            sort (Sort): Jenis pengurutan (NEWEST, RATING)
            batch_size (int): Jumlah review per batch untuk menghindari pemblokiran
            
        Returns:
            list: Daftar review yang berhasil diambil
        """
        all_reviews = []
        continuation_token = None
        remaining = count
        
        print(f"Mulai mengambil {count} review Traveloka...")
        self.logger.info(f"Mulai mengambil {count} review Traveloka")
        
        while remaining > 0:
            # Tentukan jumlah review untuk batch ini
            current_batch = min(batch_size, remaining)
            
            try:
                # Ambil review
                batch_reviews, continuation_token = reviews(
                    self.app_id,
                    lang=self.lang,
                    country=self.country,
                    sort=sort,
                    count=current_batch,
                    continuation_token=continuation_token
                )
                
                print(f"Berhasil mengambil {len(batch_reviews)} review")
                self.logger.info(f"Berhasil mengambil {len(batch_reviews)} review")
                all_reviews.extend(batch_reviews)
                remaining -= len(batch_reviews)
                
                # Jika tidak ada continuation token, berarti sudah tidak ada review lagi
                if continuation_token is None:
                    print("Tidak ada review lagi yang tersedia.")
                    self.logger.info("Tidak ada review lagi yang tersedia")
                    break
                    
                # Delay untuk menghindari rate limiting
                self._random_delay()
                
            except Exception as e:
                error_msg = f"Error saat mengambil review: {str(e)}"
                print(error_msg)
                self.logger.error(error_msg)
                # Coba delay lebih lama jika terjadi error
                time.sleep(10)
                continue
        
        print(f"Total {len(all_reviews)} review berhasil diambil.")
        self.logger.info(f"Total {len(all_reviews)} review berhasil diambil")
        return all_reviews
    
    def save_to_json(self, reviews_data, output_file=None):
        """Menyimpan review ke file JSON"""
        if output_file is None:
            output_file = f"traveloka_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Buat salinan data untuk menghindari modifikasi pada data asli
        processed_data = []
        for review in reviews_data:
            # Buat salinan review untuk menghindari perubahan pada data asli
            processed_review = review.copy()
            
            # Konversi timestamp ke format datetime yang dapat dibaca
            if isinstance(processed_review['at'], (int, float)):
                processed_review['at'] = datetime.fromtimestamp(processed_review['at']).strftime('%Y-%m-%d %H:%M:%S')
            
            if processed_review['repliedAt'] and isinstance(processed_review['repliedAt'], (int, float)):
                processed_review['repliedAt'] = datetime.fromtimestamp(processed_review['repliedAt']).strftime('%Y-%m-%d %H:%M:%S')
            
            processed_data.append(processed_review)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
        
        print(f"Review berhasil disimpan ke {output_file}")
    
    def save_to_csv(self, reviews_data, output_file=None):
        """Menyimpan review ke file CSV"""
        if output_file is None:
            output_file = f"traveloka_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Definisikan field yang akan disimpan
        fieldnames = ['reviewId', 'userName', 'userImage', 'content', 'score', 
                      'thumbsUpCount', 'reviewCreatedVersion', 'at', 'replyContent', 'repliedAt']
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for review in reviews_data:
                # Buat salinan review untuk menghindari perubahan pada data asli
                review_copy = review.copy()
                
                # Konversi timestamp ke format datetime yang dapat dibaca
                if isinstance(review_copy['at'], (int, float)):
                    review_copy['at'] = datetime.fromtimestamp(review_copy['at']).strftime('%Y-%m-%d %H:%M:%S')
                
                if review_copy['repliedAt'] and isinstance(review_copy['repliedAt'], (int, float)):
                    review_copy['repliedAt'] = datetime.fromtimestamp(review_copy['repliedAt']).strftime('%Y-%m-%d %H:%M:%S')
                
                # Filter hanya kolom yang kita butuhkan
                filtered_review = {k: review_copy.get(k, '') for k in fieldnames}
                writer.writerow(filtered_review)
        
        print(f"Review berhasil disimpan ke {output_file}")
    
    def scrape_large_data(self, total_count=1000, batch_size=20, save_interval=500, 
                     output_dir="traveloka_data", sort=Sort.NEWEST,
                     delay_min=2.0, delay_max=5.0, merge_results=False):
        """
        Mengambil data review dalam jumlah besar dengan penyimpanan bertahap
        untuk menghindari kehilangan data jika proses terganggu.
        
        Args:
            total_count (int): Total review yang akan diambil
            batch_size (int): Jumlah review per request ke Play Store
            save_interval (int): Jumlah review sebelum disimpan ke file terpisah
            output_dir (str): Direktori untuk menyimpan hasil
            sort (Sort): Jenis pengurutan review
            delay_min (float): Delay minimum antar request (detik)
            delay_max (float): Delay maksimum antar request (detik)
            merge_results (bool): Gabungkan semua hasil ke satu file di akhir
            
        Returns:
            dict: Statistik hasil scraping (jumlah, error, waktu eksekusi)
        """
        # Parameter save_interval dan merge_results masih ada untuk kompatibilitas
        # namun tidak lagi digunakan karena kita hanya menyimpan 2 file di akhir proses
        
        # Membuat timestamp untuk penamaan file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Persiapan direktori output jika belum ada
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.logger.info(f"Membuat direktori output: {output_dir}")
        
        print(f"\n{'-'*70}")
        print(f"SCRAPING DATA REVIEW TRAVELOKA DALAM JUMLAH BESAR ({total_count} review)")
        print(f"Batch size: {batch_size}, Sort: {sort.name}")
        print(f"Delay: {delay_min}-{delay_max} detik")
        print(f"Output akan disimpan di: {output_dir}")
        print(f"Format output: 2 file (JSON dan CSV) tanpa pemisahan part")
        print(f"{'-'*70}\n")
        
        # Parameter untuk tracking progress
        reviews_data = []
        error_count = 0
        continuation_token = None
        start_time = time.time()
        
        # Pengambilan data dalam batch hingga mencapai total atau token habis
        while len(reviews_data) < total_count:
            try:
                # Jumlah review yang tersisa untuk diambil
                remaining = min(batch_size, total_count - len(reviews_data))
                if remaining <= 0:
                    break
                
                # Logging progress
                self.logger.info(f"Mengambil {remaining} review (progress: {len(reviews_data)}/{total_count})")
                print(f"Mengambil batch review... ({len(reviews_data)}/{total_count})", end="\r")
                
                # Ambil batch review berikutnya
                result, continuation_token = reviews(
                    self.app_id,
                    lang=self.lang,
                    country=self.country,
                    sort=sort,
                    count=remaining,
                    count_override=remaining,
                    continuation_token=continuation_token
                )
                
                # Jika tidak ada data atau token habis
                if not result or not continuation_token:
                    self.logger.warning("Tidak ada data lebih lanjut atau token habis")
                    if not result:
                        self.logger.warning("Batch kosong diterima dari API")
                    if not continuation_token:
                        self.logger.warning("Tidak ada token lanjutan")
                    break
                
                # Tambahkan ke kumpulan data
                reviews_data.extend(result)
                
                # Terapkan delay untuk batasan rate
                delay = random.uniform(delay_min, delay_max)
                self.logger.debug(f"Menerapkan delay {delay:.2f} detik")
                time.sleep(delay)
                
            except Exception as e:
                error_count += 1
                self.logger.error(f"Error saat scraping batch: {str(e)}")
                print(f"Error: {str(e)}")
                
                # Jika terlalu banyak error, hentikan proses
                if error_count >= 5:
                    self.logger.error("Terlalu banyak error, menghentikan proses")
                    print("\nTerlalu banyak error, proses dihentikan.")
                    break
                
                # Coba lagi dengan delay lebih lama
                time.sleep(random.uniform(delay_max * 2, delay_max * 3))
        
        # Menampilkan info progres akhir
        print(f"Selesai mengambil {len(reviews_data)} review                  ")
        
        # Waktu eksekusi
        execution_time = time.time() - start_time
        
        # Simpan semua data ke file JSON
        json_filename = f"traveloka_reviews_{timestamp}.json"
        json_path = os.path.join(output_dir, json_filename)
        self.save_to_json(reviews_data, json_path)
        self.logger.info(f"Menyimpan semua data ke JSON: {json_path}")
        print(f"Semua review disimpan ke {json_path}")
        
        # Simpan semua data ke file CSV
        csv_filename = f"traveloka_reviews_{timestamp}.csv"
        csv_path = os.path.join(output_dir, csv_filename)
        self.save_to_csv(reviews_data, csv_path)
        self.logger.info(f"Menyimpan semua data ke CSV: {csv_path}")
        print(f"Semua review disimpan ke {csv_path}")
        
        # Menampilkan ringkasan hasil
        print(f"\n{'-'*70}")
        print(f"RINGKASAN SCRAPING:")
        print(f"- Total review berhasil diambil: {len(reviews_data)}")
        print(f"- Error selama proses: {error_count}")
        print(f"- Waktu eksekusi: {execution_time:.2f} detik")
        print(f"- File output:")
        print(f"  * JSON: {json_path}")
        print(f"  * CSV: {csv_path}")
        print(f"{'-'*70}\n")
        
        # Return statistik
        stats = {
            "total_reviews": len(reviews_data),
            "errors": error_count,
            "execution_time": execution_time,
            "output_json": json_path,
            "output_csv": csv_path
        }
        
        return stats
    
    def merge_data_files(self, directory, output_file=None, file_pattern="*.json"):
        """
        Menggabungkan beberapa file data menjadi satu file
        
        Args:
            directory (str): Direktori tempat file berada
            output_file (str): Nama file output
            file_pattern (str): Pola file yang akan digabungkan
        """
        import glob
        
        if output_file is None:
            output_file = f"traveloka_merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        # Cari semua file yang sesuai pola
        files = glob.glob(os.path.join(directory, file_pattern))
        
        if not files:
            print(f"Tidak ada file yang sesuai dengan pola {file_pattern} di direktori {directory}")
            return
            
        print(f"Ditemukan {len(files)} file untuk digabungkan")
        
        # Kumpulkan semua data
        all_data = []
        
        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_data.extend(data)
                    else:
                        print(f"File {file} tidak berisi array JSON, dilewati")
            except Exception as e:
                print(f"Error saat membaca file {file}: {str(e)}")
                
        # Hapus duplikat berdasarkan reviewId
        unique_reviews = {}
        for review in all_data:
            if 'reviewId' in review:
                unique_reviews[review['reviewId']] = review
                
        unique_data = list(unique_reviews.values())
        
        # Simpan ke file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unique_data, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
            
        print(f"Berhasil menggabungkan {len(files)} file dengan total {len(all_data)} review")
        print(f"Setelah menghapus duplikat, tersisa {len(unique_data)} review unik")
        print(f"Data digabungkan dan disimpan ke {output_file}")


def main():
    """Fungsi utama untuk menjalankan scraper via command line"""
    parser = argparse.ArgumentParser(
        description="Traveloka Review Scraper - Alat untuk mengambil review dari Google Play Store",
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=True
    )
    
    parser.add_argument("--mode", choices=["simple", "large"], default="simple", metavar="{simple,large}",
                        help="Mode scraping (simple: sekali jalan, large: data besar)")
    
    parser.add_argument("--count", type=int, default=100, metavar="COUNT",
                        help="Jumlah review yang akan diambil (default: 100)")
    
    parser.add_argument("--batch", type=int, default=20, metavar="BATCH",
                        help="Jumlah review per request (default: 20)")
    
    parser.add_argument("--sort", choices=["newest", "rating"], default="newest", metavar="{newest,rating}",
                        help="Urutan review (newest: terbaru, rating: peringkat) (default: newest)")
    
    parser.add_argument("--lang", default="id", metavar="LANG",
                        help="Kode bahasa (default: id)")
    
    parser.add_argument("--country", default="id", metavar="COUNTRY",
                        help="Kode negara (default: id)")
    
    parser.add_argument("--delay-min", type=float, default=2.0, metavar="DELAY_MIN",
                        help="Delay minimum antar request dalam detik (default: 2.0)")
    
    parser.add_argument("--delay-max", type=float, default=5.0, metavar="DELAY_MAX",
                        help="Delay maksimum antar request dalam detik (default: 5.0)")
    
    # Parameter untuk mode large
    parser.add_argument("--interval", type=int, default=500, metavar="INTERVAL",
                        help="(Mode large) Jumlah review per file terpisah (default: 500, tidak digunakan lagi)")
    
    parser.add_argument("--output", default="traveloka_data", metavar="OUTPUT",
                        help="(Mode large) Direktori output (default: traveloka_data)")
    
    parser.add_argument("--merge", action="store_true",
                        help="(Mode large) Gabungkan hasil setelah selesai (tidak digunakan lagi)")
    
    # Jika tidak ada argumen, tampilkan bantuan dan keluar
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    # Inisialisasi scraper
    scraper = TravelokaReviewScraper(lang=args.lang, country=args.country)
    
    # Konversi jenis urutan
    sort_type = Sort.NEWEST if args.sort == "newest" else Sort.RATING
    
    # Proses berdasarkan mode
    if args.mode == "simple":
        # Mode simple
        print(f"\nMengambil {args.count} review Traveloka dengan mode simple...")
        reviews = scraper.scrape_reviews(
            count=args.count,
            sort=sort_type,
            batch_size=args.batch,
            delay_min=args.delay_min,
            delay_max=args.delay_max
        )
        
        # Simpan hasil
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = f"traveloka_reviews_{timestamp}.json"
        csv_file = f"traveloka_reviews_{timestamp}.csv"
        
        scraper.save_to_json(reviews, json_file)
        scraper.save_to_csv(reviews, csv_file)
        
        print(f"\nSelesai! {len(reviews)} review disimpan ke:")
        print(f"- {json_file}")
        print(f"- {csv_file}")
        
    else:
        # Mode large
        print(f"\nMengambil {args.count} review Traveloka dengan mode large...")
        print(f"Output akan disimpan di direktori: {args.output}")
        
        scraper.scrape_large_data(
            total_count=args.count,
            batch_size=args.batch,
            save_interval=args.interval,  # Parameter dipertahankan untuk kompatibilitas
            output_dir=args.output,
            sort=sort_type,
            delay_min=args.delay_min,
            delay_max=args.delay_max,
            merge_results=args.merge  # Parameter dipertahankan untuk kompatibilitas
        )
        
        print("\nProses scraping selesai!")


# Contoh penggunaan
if __name__ == "__main__":
    main() 