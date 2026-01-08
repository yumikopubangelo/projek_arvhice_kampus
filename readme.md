# 🏛️ Campus Archive Platform

Platform arsip digital modern untuk mengelola dan berbagi proyek akademik mahasiswa dan dosen di lingkungan kampus. Dibangun dengan teknologi terkini untuk memfasilitasi kolaborasi akademik yang aman dan terstruktur.

## 📋 Deskripsi Proyek

Campus Archive Platform adalah sistem manajemen arsip digital yang dirancang khusus untuk institusi pendidikan tinggi. Platform ini memungkinkan mahasiswa mengupload proyek akademik mereka (seperti tugas akhir, skripsi, atau proyek kelompok) dan dosen untuk mengakses serta memberikan feedback secara terorganisir.

## ✨ Fitur Utama

### 🔐 Authentication & User Management
- **Multi-role Registration**: Registrasi untuk **Student** (mahasiswa) dan **Dosen** (dosen) dengan field khusus masing-masing
- **Secure Login**: Sistem autentikasi JWT dengan enkripsi data sensitif
- **Profile Management**: Kelola profil pengguna dengan informasi lengkap
- **Role-based Access Control**: Kontrol akses ketat berdasarkan peran pengguna

### 📁 Project Management
- **Upload Projects**: Mahasiswa dapat mengupload proyek dengan:
  - File PDF utama (wajib)
  - Metadata lengkap (judul, abstrak, penulis, tag, tahun, semester)
  - Informasi akademik (mata kuliah, kode kursus, jenis tugas)
  - Link eksternal (repository kode, dataset)
  - Advisor assignment (dosen pembimbing)
- **Project CRUD**: View, edit, dan delete proyek (hanya owner)
- **Status Tracking**: Monitoring status proyek (ongoing, completed, archived)
- **View Count**: Tracking jumlah views untuk popularitas proyek

### 🔍 Search & Discovery
- **Advanced Search**: Pencarian canggih dengan filter:
  - Teks: judul, abstrak, penulis, tag
  - Metadata: tahun, tag spesifik, level privasi, status
  - Akademik: dosen, semester, nama kelas, kode mata kuliah
- **Search Suggestions**: Auto-complete untuk judul, penulis, tag, dan kode kursus
- **Filter Options**: Dropdown filter dinamis berdasarkan data tersedia
- **Popular Tags**: Menampilkan tag yang paling sering digunakan

### 📄 File Management
- **PDF Downloads**: Download file PDF dengan tracking jumlah download
- **Supplementary Files**: Upload dan download file tambahan (gambar, data, dll.)
- **Secure Access**: Kontrol akses file berdasarkan permission dan privacy level
- **File Organization**: Sistem penyimpanan file terorganisir per proyek

### 🔒 Access Control & Privacy
- **Privacy Levels**:
  - **Public**: Terbuka untuk semua pengguna terdaftar
  - **Private**: Hanya owner dan pengguna yang diberi akses khusus
- **Access Requests**: Dosen dapat mengajukan permintaan akses ke proyek private
- **Request Management**: Owner proyek dapat approve/deny/revoke access requests
- **Access Status**: Cek status akses real-time untuk setiap proyek
- **Expiration**: Access dapat diberi batas waktu kadaluarsa

### 🎯 Dashboard & User Interface
- **Personal Dashboard**: Overview proyek dan aktivitas pengguna
- **Responsive Design**: Interface yang responsif untuk desktop dan mobile
- **Navigation**: Navbar intuitif dengan menu navigasi lengkap
- **Protected Routes**: Sistem routing dengan autentikasi

### 🛠 Technical Features
- **REST API**: Backend FastAPI dengan dokumentasi API otomatis
- **Database**: PostgreSQL dengan sistem migrasi Alembic
- **File Storage**: Sistem penyimpanan file lokal dengan struktur terorganisir
- **Containerization**: Docker setup lengkap untuk development dan production
- **Security**: JWT authentication, password hashing, data encryption
- **Monitoring**: Health checks, logging komprehensif, error handling
- **Caching**: Optimisasi performa dengan teknik caching

## 🏗️ Tech Stack

### Backend
- **Framework**: FastAPI (Python async web framework)
- **Database**: PostgreSQL dengan SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **File Handling**: Custom file service dengan secure upload
- **Migrations**: Alembic untuk database versioning

### Frontend
- **Framework**: React 18 dengan Vite build tool
- **Styling**: Tailwind CSS untuk responsive design
- **State Management**: React Context API
- **Routing**: React Router untuk SPA navigation
- **HTTP Client**: Axios untuk API communication

### Infrastructure
- **Container**: Docker & Docker Compose
- **Reverse Proxy**: Nginx untuk production deployment
- **SSL/TLS**: Let's Encrypt untuk HTTPS
- **Database**: PostgreSQL container
- **Development**: Hot reload untuk frontend dan backend

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Installation

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd campus-archive
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env dengan konfigurasi database dan secrets
   ```

3. **Build & Run**
   ```bash
   docker-compose up --build
   ```

4. **Access Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

Lihat [`docker_compose.md`](docker_compose.md) untuk setup detail dan troubleshooting.

## 📖 Usage Guide

### Untuk Mahasiswa (Student)
1. **Registrasi**: Daftar dengan NIM dan informasi akademik
2. **Upload Project**: Upload proyek dengan PDF dan metadata lengkap
3. **Manage Projects**: Edit atau hapus proyek yang sudah diupload
4. **View Access**: Lihat siapa saja yang mengakses proyek Anda

### Untuk Dosen (Lecturer)
1. **Registrasi**: Daftar dengan NIDN dan informasi departemen
2. **Browse Projects**: Cari dan filter proyek mahasiswa
3. **Request Access**: Ajukan permintaan akses untuk proyek private
4. **Download Files**: Download PDF dan file tambahan (jika diizinkan)

### Administrator
- Monitor sistem melalui logs dan health checks
- Manage database backups
- Configure SSL certificates untuk production

## 📚 API Documentation

Platform ini menyediakan API RESTful lengkap dengan dokumentasi otomatis:

- **Base URL**: `http://localhost:8000/api`
- **Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

### Main Endpoints
- `POST /api/auth/register` - Registrasi user baru
- `POST /api/auth/login` - Login dan dapatkan JWT token
- `GET /api/projects` - List projects dengan filter
- `POST /api/projects` - Upload project baru
- `GET /api/search` - Advanced search
- `POST /api/access` - Request access ke project private

## 🔧 Development

### Project Structure
```
campus-archive/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # Application entry point
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routers/        # API endpoints
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   └── alembic/            # Database migrations
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── context/        # React context
│   │   └── hooks/          # Custom hooks
│   └── public/             # Static assets
├── nginx/                   # Reverse proxy config
├── docker-compose.yml       # Docker orchestration
└── docs/                    # Documentation
```

### Key Files
- [`docker_compose.md`](docker_compose.md) - Setup dan deployment guide
- [`backend/requirements.txt`](backend/requirements.txt) - Python dependencies
- [`frontend/package.json`](frontend/package.json) - Node.js dependencies
- [`.env.example`](.env.example) - Environment variables template

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

Jika Anda mengalami masalah atau memiliki pertanyaan:

1. Check [`docker_compose.md`](docker_compose.md) untuk troubleshooting umum
2. Lihat logs container: `docker-compose logs -f`
3. Verify konfigurasi `.env` file
4. Check API documentation di `/docs`

## 🔄 Future Enhancements

- [ ] Real-time notifications untuk access requests
- [ ] Advanced analytics dan reporting
- [ ] Integration dengan LMS (Learning Management System)
- [ ] Mobile app companion
- [ ] AI-powered project categorization
- [ ] Collaborative editing features
- [ ] Backup dan disaster recovery automation

---

**Campus Archive Platform** - Transforming academic project management through digital innovation.