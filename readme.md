# Tutorial Menjalankan Aplikasi Scrapper

1. Pastikan Python Sudah Terinstal
    ```bash
    python --version
    ```
2. Buat Virtual Environment (Opsional tapi Disarankan)
    ```bash
    # Install virtualenv
    sudo pip install virtualenv --break-system-packages

    # Membuat virtualenv
    virtualenv myenv

    # Activasi virtualenv
    source myvenv/bin/activate  # Linux/macOS
    myvenv\Scripts\activate     # Windows
    ```
3. Install Dependencies
    ```bash
    pip install -r requirements.txt

    # Jika tanpa virtualenv
    pip install -r requirements.txt --break-system-packages
    ```
4. Jalankan Script
    ```bash
    python main.py
    ```

# Cara mengganti jumlah data yang ingin di scrapping

1. Ganti num_reviews = 500 
    ```python
    if __name__ == "__main__":
    start_time = time.time()
    num_reviews = 500  # Ubah ke 100, 300, atau 500 sesuai kebutuhan
    ```

# Cara mengganti Category

1. Ganti sesuai kebutuhan 

    ```python
    valid_categories = ['Username', 'Ulasan', 'Tanggal'] 
    
    # Username', 'Ulasan', 'Skor', 'Tanggal', 'Country', 'Balasan'
    ```
