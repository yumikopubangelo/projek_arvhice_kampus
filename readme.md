# 🏛️ Campus Archive Platform

Platform arsip digital modern untuk mengelola dan berbagi proyek akademik mahasiswa dan dosen di lingkungan kampus. Dibangun dengan teknologi terkini untuk memfasilitasi kolaborasi akademik yang aman dan terstruktur.

## 📋 Deskripsi Proyek

Campus Archive Platform adalah sistem manajemen arsip digital yang dirancang khusus untuk institusi pendidikan tinggi. Platform ini memungkinkan mahasiswa mengupload proyek akademik mereka (seperti tugas akhir, skripsi, atau proyek kelompok) dan dosen untuk mengakses serta memberikan feedback secara terorganisir.

## 📊 Status Proyek

| Kategori | Total Fitur | ✅ Completed | 🔄 In Progress | 📋 Planned |
|----------|-------------|--------------|----------------|------------|
| Authentication | 5 | 5 | 0 | 0 |
| Project Management | 8 | 7 | 1 | 0 |
| File Management | 6 | 4 | 0 | 2 |
| Search & Discovery | 5 | 4 | 0 | 1 |
| Access Control | 4 | 4 | 0 | 0 |
| User Interface | 8 | 7 | 0 | 1 |
| System Features | 6 | 2 | 0 | 4 |
| **TOTAL** | **42** | **33** | **1** | **8** |

**Status**: 🔄 **PHASE 1 COMPLETE** - Core features implemented and working. Ready for Phase 2 enhancements.

## ✨ Fitur Utama

### 🔐 Authentication & User Management ✅
- **Multi-role Registration**: Registrasi untuk **Student** (mahasiswa) dan **Dosen** (dosen) dengan field khusus masing-masing
- **Secure Login**: Sistem autentikasi JWT dengan enkripsi data sensitif
- **Profile Management**: Kelola profil pengguna dengan informasi lengkap
- **Role-based Access Control**: Kontrol akses ketat berdasarkan peran pengguna
- **Error Handling**: Enhanced error handling untuk Pydantic validation errors

### 📁 Project Management ✅
- **Upload Projects**: Mahasiswa dapat mengupload proyek dengan:
  - File PDF utama (wajib) - **AUTO-STORED** di `uploads/{user_id}/`
  - Metadata lengkap (judul, abstrak, penulis, tag, tahun, semester)
  - Informasi akademik (mata kuliah, kode kursus, jenis tugas)
  - Link eksternal (repository kode, dataset)
  - Advisor assignment (dosen pembimbing)
  - **Supplementary Files**: Upload multiple file tambahan dengan validasi
- **Project CRUD**: View, edit, dan delete proyek (hanya owner)
- **Status Tracking**: Monitoring status proyek (ongoing, completed, archived)
- **View Count**: Tracking jumlah views untuk popularitas proyek
- **File Cleanup**: Automatic file deletion saat project dihapus

### 🔍 Search & Discovery ✅
- **Advanced Search**: Pencarian canggih dengan filter:
  - Teks: judul, abstrak, penulis, tag
  - Metadata: tahun, tag spesifik, level privasi, status
  - Akademik: dosen, semester, nama kelas, kode mata kuliah
- **Search Suggestions**: Auto-complete untuk judul, penulis, tag, dan kode kursus
- **Filter Options**: Dropdown filter dinamis berdasarkan data tersedia
- **Popular Tags**: Menampilkan tag yang paling sering digunakan

### 📄 File Management ✅
- **User-Specific Storage**: Files otomatis tersimpan di folder `uploads/{user_id}/`
- **File Validation**: Type checking, size limits (PDF: 10MB, others: various)
- **Unique Filenames**: UUID generation mencegah konflik nama file
- **Secure Upload**: Comprehensive validation dan error handling
- **File Deletion from UI**: Hapus file tambahan langsung dari project card (owner only)
- **PDF Downloads**: Download file PDF dengan tracking jumlah download *(planned)*
- **Supplementary Files**: Upload dan download file tambahan (gambar, data, dll.) *(planned)*
- **Secure Access**: Kontrol akses file berdasarkan permission dan privacy level

### 🔒 Access Control & Privacy ✅
- **Privacy Levels**:
  - **Public**: Terbuka untuk semua pengguna terdaftar
  - **Private**: Hanya owner dan pengguna yang diberi akses khusus
  - **Advisor**: Owner + dosen pembimbing
  - **Class**: Semua mahasiswa di kelas yang sama
- **Access Requests**: Dosen dapat mengajukan permintaan akses ke proyek private
- **Request Management**: Owner proyek dapat approve/deny/revoke access requests
- **Access Status**: Cek status akses real-time untuk setiap proyek
- **Expiration**: Access dapat diberi batas waktu kadaluarsa

### 🎯 Dashboard & User Interface ✅
- **Personal Dashboard**: Overview proyek dan aktivitas pengguna
- **Responsive Design**: Interface yang responsif untuk desktop dan mobile
- **Navigation**: Navbar intuitif dengan menu navigasi lengkap
- **Protected Routes**: Sistem routing dengan autentikasi
- **Project Cards**: Display proyek dengan informasi lengkap
- **Modal Editing**: Edit project tanpa navigasi halaman
- **Custom Confirmation Modals**: Dialog konfirmasi kustom untuk aksi destruktif (seperti delete)

### 🛠 Technical Features ✅
- **REST API**: Backend FastAPI dengan dokumentasi API otomatis
- **Database**: PostgreSQL dengan sistem migrasi Alembic
- **File Storage**: Sistem penyimpanan file lokal dengan struktur `uploads/{user_id}/`
- **Containerization**: Docker setup lengkap untuk development dan production
- **Security**: JWT authentication, password hashing, data encryption
- **Monitoring**: Health checks, logging komprehensif, error handling
- **Validation**: Pydantic schemas untuk input validation

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
- **Interactive Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)
- **Complete API Reference**: [`docs/api_documentation.md`](docs/api_documentation.md)

### Main Endpoints
- `POST /api/auth/register` - Registrasi user baru (Student/Dosen)
- `POST /api/auth/login` - Login dan dapatkan JWT token
- `GET /api/auth/me` - Get user profile
- `GET /api/projects` - List projects dengan pagination & filter
- `POST /api/projects` - Upload project baru dengan files
- `GET /api/projects/{id}` - Get project detail
- `PUT /api/projects/{id}` - Update project (owner only)
- `DELETE /api/projects/{id}` - Delete project (owner only)
- `GET /api/projects/me/projects` - Get user's own projects
- `GET /api/search` - Advanced search dengan multiple filters
- `GET /api/search/suggestions` - Search autocomplete
- `POST /api/access` - Request access ke project private
- `GET /api/access/my-requests` - View access requests
- `GET /api/files/{project_id}/pdf` - Download PDF *(planned)*
- `GET /api/health` - Health check endpoint

## 🔧 Development

### Project Structure
```
campus-archive/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # Application entry point
│   │   ├── config.py       # Configuration management
│   │   ├── database.py     # Database connection
│   │   ├── models/         # SQLAlchemy models
│   │   │   ├── user.py     # User model
│   │   │   ├── project.py  # Project model
│   │   │   └── access_request.py # Access request model
│   │   ├── routers/        # API endpoints
│   │   │   ├── auth.py     # Authentication endpoints
│   │   │   ├── projects.py # Project CRUD endpoints
│   │   │   ├── search.py   # Search endpoints
│   │   │   ├── access.py   # Access control endpoints
│   │   │   └── files.py    # File download endpoints
│   │   ├── schemas/        # Pydantic schemas
│   │   │   ├── user.py     # User validation schemas
│   │   │   ├── project.py  # Project validation schemas
│   │   │   └── access_request.py # Access request schemas
│   │   ├── services/       # Business logic
│   │   │   ├── auth_service.py     # Authentication logic
│   │   │   ├── project_service.py  # Project business logic
│   │   │   ├── file_service.py     # File handling logic
│   │   │   └── __init__.py
│   │   ├── dependencies/   # FastAPI dependencies
│   │   ├── utils/          # Utilities
│   │   │   ├── encryption.py # Data encryption
│   │   │   └── password.py  # Password hashing
│   │   └── __init__.py
│   ├── alembic/            # Database migrations
│   │   ├── versions/       # Migration files
│   │   └── env.py          # Migration environment
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend container config
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   │   ├── Navbar.jsx          # Navigation bar
│   │   │   ├── ProjectCard.jsx     # Project display card
│   │   │   ├── ProjectEditModal.jsx # Edit project modal
│   │   │   ├── ConfirmationModal.jsx # Custom confirmation dialog
│   │   │   ├── FileUpload.jsx      # File upload component
│   │   │   ├── ProtectedRoute.jsx  # Route protection
│   │   │   ├── SearchBar.jsx       # Search component
│   │   ├── pages/          # Page components
│   │   │   ├── LandingPage.jsx    # Welcome page
│   │   │   ├── LoginPage.jsx      # Login form
│   │   │   ├── RegisterPage.jsx   # Registration form
│   │   │   ├── DashboardPage.jsx  # Main dashboard
│   │   │   ├── UploadPage.jsx     # Project upload form
│   │   │   ├── ProjectDetailPage.jsx # Project details
│   │   │   ├── SearchPage.jsx     # Search results
│   │   │   ├── TestPage.jsx       # Testing page
│   │   │   └── HomePage.jsx       # Home page
│   │   ├── context/        # React context
│   │   │   └── AuthContext.jsx    # Authentication context
│   │   ├── hooks/          # Custom hooks
│   │   │   ├── useAuth.js         # Authentication hook
│   │   │   └── useProjects.js     # Projects hook
│   │   ├── api/            # API client
│   │   │   └── client.js          # Axios client config
│   │   ├── utils/          # Utilities
│   │   │   ├── formatDate.js      # Date formatting
│   │   │   └── encryption.js      # Client-side encryption
│   │   └── styles/         # Additional styles
│   ├── public/             # Static assets
│   ├── package.json        # Node.js dependencies
│   └── Dockerfile          # Frontend container config
├── uploads/                # File storage directory
│   ├── 1/                 # User ID 1 files
│   ├── 2/                 # User ID 2 files
│   └── {user_id}/         # User-specific folders
├── nginx/                  # Reverse proxy config
│   ├── nginx.conf          # Main nginx config
│   └── conf.d/             # Site configurations
├── docs/                   # Documentation
│   ├── api_documentation.md    # Complete API reference
│   └── features.md             # Feature status & roadmap
├── docker-compose.yml      # Docker orchestration
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── docker_compose.md      # Docker setup guide
├── TODO.md                # Current tasks & issues
└── README.md              # This file
```

### Key Files & Documentation
- [`docs/features.md`](docs/features.md) - **NEW**: Complete feature status & development roadmap
- [`docs/api_documentation.md`](docs/api_documentation.md) - Complete API reference
- [`docker_compose.md`](docker_compose.md) - Setup dan deployment guide
- [`backend/requirements.txt`](backend/requirements.txt) - Python dependencies
- [`frontend/package.json`](frontend/package.json) - Node.js dependencies
- [`.env.example`](.env.example) - Environment variables template
- [`TODO.md`](TODO.md) - Current development tasks & known issues

### Recent Updates (January 2026)
- ✅ **File Deletion**: Pengguna sekarang dapat menghapus file tambahan langsung dari kartu proyek.
- ✅ **Custom Confirmation Modals**: Mengganti dialog browser bawaan dengan modal konfirmasi kustom untuk pengalaman pengguna yang lebih baik dan lebih aman saat menghapus.
- ✅ **Bug Fixes**: Memperbaiki bug kritis pada penanganan error saat upload file dan pembaruan proyek.
- ✅ **File Upload Enhancement**: Files now automatically stored in user-specific folders (`uploads/{user_id}/`)
- ✅ **User-Specific Storage**: Each user gets dedicated folder with unique filenames (UUID)
- ✅ **Enhanced Error Handling**: Improved Pydantic validation error display in frontend
- ✅ **File Validation**: Comprehensive validation for file types, sizes, and security
- ✅ **Project Deletion**: Automatic cleanup of associated files when projects are deleted
- ✅ **Feature Documentation**: Complete feature tracking and roadmap documentation

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

## 🔄 Development Roadmap

### Phase 2 - Enhanced Features (Next Priority)
- [ ] **File Download Functionality**: Implement PDF and supplementary file downloads
- [ ] **File Preview**: PDF viewer and image preview in browser
- [ ] **Advanced Search UI**: Enhanced search interface with saved searches
- [ ] **Email Notifications**: Registration confirmation, access request notifications
- [ ] **System Statistics**: User count, project statistics, download tracking

### Phase 3 - Advanced Features (Future)
- [ ] **Admin Panel**: User management, system monitoring interface
- [ ] **Backup System**: Automated database and file backups
- [ ] **Monitoring & Logging**: Sentry integration, advanced error tracking
- [ ] **Statistics Dashboard**: Comprehensive analytics and reporting

### Long-term Vision
- [ ] **Real-time Notifications**: WebSocket notifications for access requests
- [ ] **LMS Integration**: Integration dengan Learning Management Systems
- [ ] **Mobile App**: Companion mobile application
- [ ] **AI Features**: AI-powered project categorization and recommendations
- [ ] **Collaborative Features**: Multi-user editing and commenting
- [ ] **Advanced Backup**: Disaster recovery automation

### Current Status
- **Phase 1**: ✅ **COMPLETE** - Core platform with user-specific file storage
- **Phase 2**: 🔄 **NEXT** - File downloads and enhanced user experience
- **Phase 3**: 📋 **PLANNED** - Advanced administrative and monitoring features

---

## 📈 Project Metrics

- **Total Features**: 42
- **Completed**: 33 (79%)
- **In Progress**: 1 (2%)
- **Planned**: 8 (19%)
- **Core Functionality**: ✅ **PRODUCTION READY**
- **File Storage**: ✅ **USER-ISOLATED & SECURE**
- **API Coverage**: ✅ **COMPLETE**
- **Frontend Coverage**: ✅ **FULLY FUNCTIONAL**

---

**Campus Archive Platform** - Transforming academic project management through digital innovation.

*Last updated: January 2026 | Phase 1 Complete ✅*