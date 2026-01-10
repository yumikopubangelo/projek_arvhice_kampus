# 📚 Development Environment Setup Guide

Selamat datang di Campus Archive Platform! Panduan ini akan memandu Anda melalui proses lengkap untuk menyiapkan lingkungan pengembangan lokal Anda.

## 1. System Prerequisites

Sebelum memulai, pastikan sistem Anda telah terinstal perangkat lunak berikut:

- **Git**: Untuk mengkloning repositori.
- **Docker**: Versi `20.10` atau lebih tinggi.
- **Docker Compose**: Versi `2.0` atau lebih tinggi.
- **Code Editor**: Visual Studio Code, JetBrains Rider, atau editor pilihan Anda.

## 2. Initial Project Setup

### Langkah 1: Clone Repository
Buka terminal Anda dan kloning repositori proyek ke direktori lokal Anda.

```bash
git clone https://github.com/yumikopubangelo/projek_arvhice_kampus
cd campus-archive
```

### Langkah 2: Konfigurasi Environment Variables
File `.env` digunakan untuk menyimpan semua variabel konfigurasi dan rahasia. File ini tidak dilacak oleh Git demi keamanan.

1.  **Buat file `.env`**: Salin dari contoh yang disediakan.
    ```bash
    cp .env.example .env
    ```

2.  **Edit file `.env`**: Buka file `.env` yang baru dibuat dengan editor teks Anda. Anda **wajib** mengubah beberapa nilai agar sesuai dengan lingkungan lokal Anda.

    **Konfigurasi Kritis untuk Lokal:**

    - **`SECRET_KEY`**: Generate kunci rahasia baru untuk keamanan sesi JWT.
      ```bash
      # Jalankan perintah ini di terminal dan salin hasilnya ke SECRET_KEY
      openssl rand -hex 32
      ```

    - **`POSTGRES_PASSWORD`**: Ganti dengan password yang kuat untuk database lokal Anda.
      ```env
      POSTGRES_PASSWORD=password_lokal_yang_aman
      ```

    - **`DATABASE_URL`**: Pastikan password di URL ini **sama** dengan `POSTGRES_PASSWORD`.
      ```env
      DATABASE_URL=postgresql://archive_user:password_lokal_yang_aman@postgres:5432/campus_archive_db
      ```
    
    - **`ALLOWED_ORIGINS`**: Untuk pengembangan lokal, arahkan ke URL frontend Vite.
      ```env
      ALLOWED_ORIGINS=http://localhost:5173
      ```

    - **`VITE_API_URL`**: Arahkan ke URL backend lokal yang diakses dari browser.
      ```env
      VITE_API_URL=http://localhost:8000
      ```

    - **`DOMAIN`**: Untuk lokal, cukup gunakan `localhost`.
      ```env
      DOMAIN=localhost
      ```

## 3. Menjalankan Aplikasi
Setelah `.env` dikonfigurasi, Anda siap menjalankan seluruh platform menggunakan Docker Compose.

```bash
# Perintah ini akan membangun image (jika belum ada) dan menjalankan semua layanan.
docker-compose up --build

# Untuk menjalankan di background (detached mode)
docker-compose up --build -d
```
Proses build pertama kali mungkin memakan waktu beberapa menit. Setelah selesai, semua layanan akan berjalan.

## 4. Mengakses Layanan
Berikut adalah endpoint utama untuk lingkungan pengembangan lokal:

| Layanan | URL | Deskripsi |
| :--- | :--- | :--- |
| **Frontend App** | `http://localhost:5173` | Aplikasi React yang diakses oleh pengguna. |
| **Backend API** | `http://localhost:8000` | Endpoint utama API FastAPI. |
| **API Docs (Swagger)**| `http://localhost:8000/docs` | Dokumentasi API interaktif. |
| **Database** | `localhost:5432` | Port database PostgreSQL (untuk diakses dari DBeaver, dll). |

## 5. Alur Kerja Pengembangan Lokal

### Melihat Logs
Untuk memonitor output dari semua layanan atau mendebug masalah:
```bash
# Melihat log dari semua container secara real-time
docker-compose logs -f

# Melihat log dari layanan spesifik (misal: backend)
docker-compose logs -f backend
```

### Migrasi Database (Alembic)
Backend menggunakan Alembic untuk mengelola skema database.

- **Membuat Migrasi Baru**: Jika Anda mengubah model SQLAlchemy di `backend/app/models/`, Anda perlu membuat file migrasi baru.
  ```bash
  docker-compose exec backend alembic revision --autogenerate -m "Deskripsi perubahan model"
  ```
- **Menjalankan Migrasi**: `docker-compose.yml` sudah dikonfigurasi untuk menjalankan migrasi secara otomatis saat backend container dimulai. Namun, jika perlu dijalankan manual:
  ```bash
  docker-compose exec backend alembic upgrade head
  ```

### Menambah Dependensi
- **Backend (Python)**:
  1. Tambahkan nama paket ke `backend/requirements.txt`.
  2. Bangun ulang image backend: `docker-compose build backend`

- **Frontend (Node.js)**:
  1. Masuk ke dalam container frontend: `docker-compose exec frontend sh`
  2. Jalankan `npm install <nama-paket>`. Ini akan memperbarui `package.json` dan `package-lock.json`.
  3. Keluar dari container (`exit`) dan bangun ulang image: `docker-compose build frontend`.

## 6. Penjelasan Environment Variables (`.env`)

Tabel ini menjelaskan setiap variabel di file `.env.example`.

| Variabel | Deskripsi | Contoh Nilai Lokal |
| :--- | :--- | :--- |
| `ENVIRONMENT` | Mode aplikasi (`development` atau `production`). | `development` |
| `DEBUG` | Mengaktifkan mode debug FastAPI. | `True` |
| `DOMAIN` | Domain utama aplikasi. | `localhost` |
| `POSTGRES_USER` | Username untuk database PostgreSQL. | `archive_user` |
| `POSTGRES_PASSWORD`| Password untuk user database. **Harus diubah**. | `password_rahasia` |
| `POSTGRES_DB` | Nama database. | `campus_archive_db` |
| `DATABASE_URL` | URL koneksi lengkap untuk SQLAlchemy. | `postgresql://...` |
| `SECRET_KEY` | Kunci rahasia untuk enkripsi JWT. **Wajib diganti**. | Hasil dari `openssl rand -hex 32` |
| `ALGORITHM` | Algoritma enkripsi JWT. | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| Durasi token JWT sebelum kedaluwarsa. | `30` atau `1440` (untuk dev) |
| `ALLOWED_ORIGINS`| Daftar origin yang diizinkan CORS (pisahkan dengan koma). | `http://localhost:5173` |
| `VITE_API_URL` | URL base API yang digunakan oleh frontend React. | `http://localhost:8000` |
| `UPLOAD_DIR` | Direktori di dalam container backend untuk menyimpan file. | `/app/uploads` |
| `MAX_UPLOAD_SIZE`| Ukuran file upload maksimal dalam bytes. | `10485760` (10 MB) |
| `ALLOWED_EXTENSIONS`| Ekstensi file yang diizinkan (pisahkan dengan koma). | `pdf,zip,docx` |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | Konfigurasi untuk mengirim email (opsional). | Dibiarkan kosong |

## 7. Troubleshooting Masalah Umum

- **Error: "Port is already allocated"**
  - **Penyebab**: Port yang dibutuhkan (misal: 8000, 5173, 5432) sudah digunakan oleh aplikasi lain.
  - **Solusi**: Hentikan aplikasi yang menggunakan port tersebut, atau ubah port di `docker-compose.yml`. Misalnya, ubah `"5173:5173"` menjadi `"5174:5173"`.

- **Error: Backend gagal terhubung ke Database**
  - **Penyebab**: `POSTGRES_PASSWORD` tidak cocok dengan password di `DATABASE_URL`, atau container `postgres` gagal dimulai.
  - **Solusi**:
    1. Periksa `docker-compose logs postgres` untuk melihat error pada database.
    2. Pastikan password di `.env` sudah benar dan konsisten.
    3. Hapus volume Docker jika database korup: `docker-compose down -v`, lalu coba lagi.

- **Error: 502 Bad Gateway di Browser**
  - **Penyebab**: Container `backend` tidak berjalan atau crash.
  - **Solusi**: Periksa log backend: `docker-compose logs -f backend`. Cari traceback error Python.

- **Error: `npm` atau `pip` gagal saat build**
  - **Penyebab**: Masalah jaringan atau paket yang tidak tersedia.
  - **Solusi**: Coba jalankan `docker-compose build --no-cache` untuk membangun ulang dari awal. Pastikan koneksi internet stabil.
