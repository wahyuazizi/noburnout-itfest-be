## Repositori Frontend

Frontend untuk proyek ini dapat ditemukan di: [https://github.com/maulidihidayat/frontend-itfest](https://github.com/maulidihidayat/frontend-itfest)

# NoBurnout ITFest Backend

Repositori ini berisi layanan backend untuk proyek NoBurnout ITFest. Dibangun menggunakan FastAPI.

## Memulai

Ikuti petunjuk ini untuk mengatur dan menjalankan proyek secara lokal atau menggunakan Docker.

### Prasyarat

- Python 3.11 atau lebih tinggi
- pip (penginstal paket Python) atau uv
- Docker (opsional, untuk deployment dalam kontainer)

### Pengaturan Pengembangan Lokal

1.  **Kloning repositori:**
    ```bash
    git clone https://github.com/your-username/noburnout-itfest-be.git
    cd noburnout-itfest-be
    ```

2.  **Buat dan aktifkan virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instal dependensi:**
    Menggunakan `uv` (direkomendasikan jika terinstal):
    ```bash
    uv pip install -r requirements.txt
    ```
    Atau menggunakan `pip`:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Variabel Lingkungan:**
    Buat file `.env` di direktori root dengan menyalin `.env.example` dan mengisi nilai-nilai yang diperlukan.
    ```bash
    cp .env.example .env
    ```
    Edit file `.env` dengan konfigurasi spesifik Anda (misalnya, kredensial database, kunci API).

5.  **Jalankan aplikasi:**
    ```bash
    uvicorn app.main:app --reload
    ```

### Menjalankan dengan Docker

1.  **Bangun image Docker:**
    ```bash
    docker build -t noburnout-itfest-be .
    ```

2.  **Jalankan kontainer Docker:**
    Pastikan untuk menyediakan variabel lingkungan Anda. Anda dapat me-mount file `.env` atau meneruskannya secara langsung.
    Contoh dengan file `.env` (pastikan `.env` ada di root proyek):
    ```bash
    docker run -d --env-file .env -p 8000:8000 noburnout-itfest-be
    ```
    API akan dapat diakses di `http://localhost:8000`.

## Struktur Proyek

-   `app/`: Berisi kode aplikasi utama.
    -   `api/`: Rute dan endpoint API.
    -   `models/`: Model database.
    -   `schemas/`: Skema Pydantic untuk validasi permintaan/respons.
    -   `services/`: Logika bisnis dan integrasi layanan eksternal.
    -   `utils/`: Fungsi utilitas.
-   `Dockerfile`: Dockerfile untuk membangun image aplikasi.
-   `requirements.txt`: Dependensi Python.
-   `pyproject.toml`: Metadata proyek dan dependensi (alternatif untuk requirements.txt).
-   `.env.example`: Contoh variabel lingkungan.

---