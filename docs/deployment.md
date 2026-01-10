# 🚀 Production Deployment Guide

Panduan ini menyediakan langkah-langkah detail untuk men-deploy Campus Archive Platform ke lingkungan produksi menggunakan Docker pada server Linux.

## 1. Prasyarat Server

- **Sistem Operasi**: Server Linux (direkomendasikan Ubuntu 22.04 LTS).
- **Domain Name**: Nama domain yang sudah diarahkan ke IP publik server Anda.
- **Perangkat Lunak Terinstal**:
  - Docker (`20.10+`)
  - Docker Compose (`2.0+`)
  - Git
  - Certbot (untuk SSL)

### Instalasi Perangkat Lunak
Jika server Anda masih baru, instal perangkat lunak yang diperlukan:
```bash
# Update sistem
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Install Certbot
sudo apt install certbot -y

# (Opsional) Buat user non-root untuk deployment
sudo adduser deploy
sudo usermod -aG docker deploy
su - deploy
```

## 2. Konfigurasi Awal Server

### Langkah 1: Clone Repository
```bash
git clone https://github.com/yumikopubangelo/projek_arvhice_kampus
cd campus-archive
```

### Langkah 2: Konfigurasi `.env` untuk Produksi
Salin file contoh dan sesuaikan untuk lingkungan produksi.

```bash
cp .env.example .env
nano .env
```

**Variabel yang Wajib Diubah untuk Produksi:**

- **`ENVIRONMENT`**: Set ke `production`.
- **`DEBUG`**: Set ke `False`.
- **`DOMAIN`**: Masukkan nama domain Anda (misal: `arsip.kampus.ac.id`).
- **`SECRET_KEY`**: Generate kunci yang sangat rahasia.
  ```bash
  # Jalankan di terminal dan salin hasilnya
  openssl rand -hex 32
  ```
- **`POSTGRES_PASSWORD`**: Gunakan password yang kuat dan unik.
- **`DATABASE_URL`**: Pastikan password di URL ini sama dengan `POSTGRES_PASSWORD`.
- **`ALLOWED_ORIGINS`**: Arahkan ke domain frontend Anda (dengan `https://`).
  ```env
  ALLOWED_ORIGINS=https://arsip.kampus.ac.id
  ```
- **`VITE_API_URL`**: Arahkan ke endpoint API di domain Anda.
  ```env
  VITE_API_URL=https://arsip.kampus.ac.id/api
  ```
- **`SMTP_...`**: Isi dengan konfigurasi SMTP server Anda untuk pengiriman email.

## 3. Konfigurasi Nginx dan SSL/TLS

### Langkah 1: Dapatkan Sertifikat SSL
Gunakan Certbot untuk mendapatkan sertifikat SSL dari Let's Encrypt. Pastikan domain Anda sudah mengarah ke IP server.

```bash
# Hentikan sementara layanan lain yang mungkin menggunakan port 80
# (docker-compose belum berjalan, jadi seharusnya aman)

sudo certbot certonly --standalone \
  -d arsip.kampus.ac.id \
  --email admin@kampus.ac.id \
  --agree-tos \
  --non-interactive
```
Sertifikat akan tersimpan di `/etc/letsencrypt/live/arsip.kampus.ac.id/`.

### Langkah 2: Salin Sertifikat ke Proyek
Nginx di dalam container Docker perlu mengakses sertifikat ini. Salin ke direktori proyek.
```bash
# Buat direktori ssl jika belum ada
mkdir -p nginx/ssl/live/arsip.kampus.ac.id

# Salin sertifikat
sudo cp /etc/letsencrypt/live/arsip.kampus.ac.id/* nginx/ssl/live/arsip.kampus.ac.id/
```

### Langkah 3: Konfigurasi Nginx
File `nginx/conf.d/campus-archive.conf` sudah dikonfigurasi untuk menggunakan sertifikat ini dan mengarahkan HTTP ke HTTPS. Pastikan `server_name` di dalam file tersebut sesuai dengan domain Anda.

## 4. Menjalankan Aplikasi di Produksi

Dengan semua konfigurasi di tempat, Anda dapat menjalankan aplikasi.

```bash
# Bangun image dan jalankan semua layanan di background
docker-compose up --build -d
```

### Verifikasi Deployment
Periksa apakah semua container berjalan dengan status `Up`.
```bash
docker-compose ps
```
Anda seharusnya melihat `backend`, `frontend`, `postgres`, dan `nginx` berjalan. Akses `https://<domain-anda>` untuk memastikan aplikasi dapat diakses.

## 5. Manajemen Database

### Menjalankan Migrasi
Meskipun `docker-compose.yml` dikonfigurasi untuk menjalankan migrasi saat startup, terkadang Anda perlu menjalankannya secara manual setelah deployment.
```bash
docker-compose exec backend alembic upgrade head
```

### Prosedur Backup Database
Sangat penting untuk melakukan backup database secara rutin.

**Backup Manual:**
```bash
# Buat direktori backup jika belum ada
mkdir -p backups/db

# Lakukan backup database dan kompres
docker-compose exec -T postgres pg_dump -U archive_user campus_archive_db \
  | gzip > backups/db/backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

**Restore Manual:**
```bash
# Hentikan layanan yang bergantung pada database
docker-compose stop backend

# Restore dari file backup
gunzip < backups/db/backup_namafile.sql.gz | \
  docker-compose exec -T postgres psql -U archive_user -d campus_archive_db

# Restart layanan
docker-compose start backend
```

## 6. Backup File Uploads
Selain database, Anda juga harus mem-backup direktori `uploads/`.

**Backup Direktori `uploads`:**
```bash
# Buat direktori backup jika belum ada
mkdir -p backups/files

# Arsipkan dan kompres seluruh direktori uploads
tar -czf backups/files/uploads_$(date +%Y%m%d).tar.gz uploads/
```

**Restore Direktori `uploads`:**
```bash
# Ekstrak arsip ke lokasi semula
tar -xzf backups/files/uploads_namafile.tar.gz
```

## 7. Monitoring dan Pemeliharaan

### Melihat Logs
Gunakan `docker-compose logs` untuk memantau aktivitas dan mendiagnosis masalah.
```bash
# Tampilkan log dari semua layanan secara real-time
docker-compose logs -f

# Tampilkan 200 baris log terakhir dari backend
docker-compose logs --tail=200 backend
```

### Memonitor Penggunaan Sumber Daya
Gunakan `docker stats` untuk melihat penggunaan CPU, memori, dan jaringan per container.
```bash
docker stats
```

### Memperbarui Aplikasi
Untuk men-deploy versi baru dari kode Anda:
```bash
# 1. Tarik perubahan terbaru dari Git
git pull origin main

# 2. Bangun ulang image dan restart layanan
# Docker akan me-restart container yang definisinya berubah
docker-compose up --build -d

# 3. Jalankan migrasi database jika ada perubahan skema
docker-compose exec backend alembic upgrade head

# 4. Hapus image lama yang tidak terpakai
docker image prune -f
```

### Perpanjangan Sertifikat SSL
Sertifikat Let's Encrypt berlaku selama 90 hari. Siapkan cron job untuk memperbaruinya secara otomatis.
```bash
# Tambahkan cron job
sudo crontab -e

# Tambahkan baris ini untuk menjalankan perpanjangan setiap hari jam 2 pagi
# dan me-restart Nginx jika ada pembaruan.
0 2 * * * certbot renew --quiet && docker-compose -f /path/to/your/project/docker-compose.yml restart nginx
```
Pastikan untuk mengganti `/path/to/your/project/` dengan path absolut ke direktori proyek Anda.
