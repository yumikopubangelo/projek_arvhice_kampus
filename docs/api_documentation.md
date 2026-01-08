# 📚 Campus Archive Platform - API Documentation

Dokumentasi lengkap untuk REST API Campus Archive Platform. API ini dibangun dengan FastAPI dan menyediakan endpoint untuk manajemen proyek akademik, autentikasi, pencarian, dan kontrol akses.

## 🔗 Base URL
```
Production: https://yourdomain.com/api
Development: http://localhost:8000/api
```

## 🔐 Authentication
API menggunakan JWT (JSON Web Token) untuk autentikasi. Sertakan token dalam header:
```
Authorization: Bearer <your_jwt_token>
```

### Mendapatkan Token
Gunakan endpoint `/auth/login` untuk mendapatkan JWT token.

---

## 👤 Authentication Endpoints

### POST /auth/register
Registrasi user baru (Student atau Dosen).

**Request Body:**
```json
{
  "email": "student@university.edu",
  "password": "securepassword123",
  "full_name": "John Doe",
  "role": "student",
  "student_id": "12345678",
  "phone": "081234567890"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "student@university.edu",
  "full_name": "John Doe",
  "role": "student",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**
- `400`: Email sudah terdaftar atau data tidak valid
- `422`: Validation error (field required, format salah)

### POST /auth/login
Login dan dapatkan JWT token.

**Request Body:**
```json
{
  "email": "student@university.edu",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "student@university.edu",
    "full_name": "John Doe",
    "role": "student"
  }
}
```

**Error Responses:**
- `401`: Email atau password salah
- `403`: Akun dinonaktifkan

### GET /auth/me
Dapatkan informasi profil user saat ini.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "student@university.edu",
  "full_name": "John Doe",
  "role": "student",
  "student_id": "12345678",
  "department": null,
  "title": null,
  "phone": "081234567890",
  "is_active": true,
  "last_login": "2024-01-01T10:00:00Z"
}
```

---

## 📁 Projects Endpoints

### POST /projects
Upload proyek baru (khusus Student).

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `title`: string (required) - Judul proyek
- `abstract`: string (required) - Abstrak proyek
- `authors`: string (required) - Penulis (comma-separated)
- `tags`: string (required) - Tag (comma-separated)
- `year`: integer (required) - Tahun proyek
- `semester`: string (optional) - Semester
- `class_name`: string (optional) - Nama kelas
- `course_code`: string (optional) - Kode mata kuliah
- `assignment_type`: string (optional) - Jenis tugas
- `privacy_level`: string (default: "private") - "public" atau "private"
- `code_repo_url`: string (optional) - URL repository kode
- `dataset_url`: string (optional) - URL dataset
- `advisor_id`: integer (optional) - ID dosen pembimbing
- `pdf_file`: file (required) - File PDF proyek

**Response (201):**
```json
{
  "id": 1,
  "title": "Analisis Big Data untuk Prediksi Harga Saham",
  "abstract": "Proyek ini menganalisis...",
  "authors": ["John Doe", "Jane Smith"],
  "tags": ["big data", "machine learning", "finance"],
  "year": 2024,
  "semester": "Genap",
  "privacy_level": "private",
  "status": "ongoing",
  "uploaded_by": 1,
  "advisor_id": 2,
  "view_count": 0,
  "download_count": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "uploader": {
    "id": 1,
    "full_name": "John Doe",
    "email": "student@university.edu"
  }
}
```

### GET /projects
Dapatkan daftar proyek dengan filter.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `year`: integer (optional) - Filter berdasarkan tahun
- `tag`: string (optional) - Filter berdasarkan tag
- `privacy_level`: string (optional) - "public" atau "private"
- `skip`: integer (default: 0) - Skip results
- `limit`: integer (default: 20, max: 100) - Limit results

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Analisis Big Data...",
    "abstract_preview": "Proyek ini menganalisis...",
    "authors": ["John Doe"],
    "tags": ["big data", "ml"],
    "year": 2024,
    "privacy_level": "public",
    "uploaded_by": 1,
    "view_count": 15,
    "uploader": {
      "id": 1,
      "full_name": "John Doe",
      "email": "student@university.edu"
    }
  }
]
```

### GET /projects/{project_id}
Dapatkan detail proyek spesifik.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `project_id`: integer (required) - ID proyek

**Response (200):** (sama dengan POST response)

**Error Responses:**
- `404`: Proyek tidak ditemukan
- `403`: Tidak memiliki akses ke proyek ini

### PUT /projects/{project_id}
Update proyek (khusus owner).

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Path Parameters:**
- `project_id`: integer (required) - ID proyek

**Request Body:**
```json
{
  "title": "Updated Title",
  "abstract": "Updated abstract...",
  "tags": ["updated", "tags"],
  "privacy_level": "public"
}
```

### DELETE /projects/{project_id}
Hapus proyek (khusus owner).

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `project_id`: integer (required) - ID proyek

**Response (204):** No Content

### GET /projects/me/projects
Dapatkan proyek yang diupload oleh user saat ini.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):** Array of projects

---

## 🔍 Search Endpoints

### GET /search
Pencarian proyek dengan filter canggih.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `q`: string (optional) - Query pencarian (judul, abstrak, penulis, tag)
- `year`: integer (optional)
- `tag`: string (optional)
- `privacy_level`: string (optional)
- `status`: string (optional)
- `uploader_id`: integer (optional)
- `advisor_id`: integer (optional)
- `semester`: string (optional)
- `class_name`: string (optional)
- `course_code`: string (optional)
- `skip`: integer (default: 0)
- `limit`: integer (default: 20)

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Big Data Analysis",
    "abstract_preview": "This project analyzes...",
    "authors": ["John Doe"],
    "tags": ["big data", "analytics"],
    "year": 2024,
    "semester": "Genap",
    "status": "ongoing",
    "privacy_level": "public",
    "uploaded_by": 1,
    "advisor_id": 2,
    "view_count": 25,
    "created_at": "2024-01-01T00:00:00Z",
    "uploader_name": "John Doe",
    "advisor_name": "Dr. Jane Smith"
  }
]
```

### GET /search/suggestions
Dapatkan saran pencarian.

**Query Parameters:**
- `q`: string (required, min: 1) - Partial query

**Response (200):**
```json
{
  "titles": ["Big Data", "Machine Learning"],
  "authors": ["John Doe", "Jane Smith"],
  "tags": ["python", "data science"],
  "courses": ["CS101", "DS201"]
}
```

### GET /search/filters
Dapatkan opsi filter yang tersedia.

**Response (200):**
```json
{
  "years": [2022, 2023, 2024],
  "tags": [
    {"tag": "machine learning", "count": 15},
    {"tag": "python", "count": 12}
  ],
  "semesters": ["Ganjil", "Genap"],
  "course_codes": ["CS101", "DS201"],
  "class_names": ["Data Science", "AI Fundamentals"]
}
```

### POST /search/advanced
Pencarian advanced dengan structured parameters.

**Request Body:**
```json
{
  "query": "machine learning",
  "year": 2024,
  "tag": "python",
  "privacy_level": "public",
  "skip": 0,
  "limit": 10
}
```

### GET /search/popular-tags
Dapatkan tag paling populer.

**Query Parameters:**
- `limit`: integer (default: 20, max: 100)

**Response (200):**
```json
[
  {"tag": "machine learning", "count": 25},
  {"tag": "python", "count": 20}
]
```

---

## 🔒 Access Control Endpoints

### POST /access
Buat permintaan akses ke proyek private (khusus Dosen).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "project_id": 1,
  "message": "Saya ingin mengakses proyek ini untuk keperluan penelitian"
}
```

**Response (201):**
```json
{
  "id": 1,
  "project_id": 1,
  "requester_id": 2,
  "message": "Saya ingin mengakses...",
  "status": "pending",
  "requested_at": "2024-01-01T00:00:00Z"
}
```

### GET /access/my-requests
Dapatkan permintaan akses yang dibuat user saat ini.

**Query Parameters:**
- `status_filter`: string (optional) - "pending", "approved", "denied"

### GET /access/for-my-projects
Dapatkan permintaan akses untuk proyek milik user saat ini.

**Query Parameters:**
- `status_filter`: string (optional)

### GET /access/{request_id}
Dapatkan detail permintaan akses spesifik.

**Path Parameters:**
- `request_id`: integer (required)

### POST /access/{request_id}/respond
Respond permintaan akses (khusus owner proyek).

**Path Parameters:**
- `request_id`: integer (required)

**Request Body:**
```json
{
  "action": "approve", // "approve", "deny", "revoke"
  "response_message": "Akses diberikan untuk keperluan penelitian",
  "expires_at": "2024-12-31T23:59:59Z" // optional
}
```

### DELETE /access/{request_id}
Batalkan permintaan akses (khusus requester, status pending).

### GET /access/check/{project_id}
Cek status akses user saat ini untuk proyek tertentu.

**Response (200):**
```json
{
  "project_id": 1,
  "has_access": true,
  "request_status": "approved",
  "privacy_level": "private"
}
```

---

## 📄 Files Endpoints

### GET /files/{project_id}/pdf
Download file PDF proyek.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `project_id`: integer (required)

**Response:** File PDF download

**Error Responses:**
- `403`: Tidak memiliki akses download
- `404`: File tidak ditemukan

### GET /files/{project_id}/supplementary/{filename}
Download file supplementary.

**Path Parameters:**
- `project_id`: integer (required)
- `filename`: string (required)

---

## 🏥 Health Check

### GET /health
Cek status API.

**Response (200):**
```json
{
  "status": "ok",
  "message": "API is working"
}
```

---

## 📊 Response Codes

- `200`: OK - Request berhasil
- `201`: Created - Resource berhasil dibuat
- `204`: No Content - Request berhasil, tidak ada response body
- `400`: Bad Request - Request tidak valid
- `401`: Unauthorized - Token tidak valid atau missing
- `403`: Forbidden - Tidak memiliki permission
- `404`: Not Found - Resource tidak ditemukan
- `422`: Unprocessable Entity - Validation error
- `500`: Internal Server Error - Error server

## 🔧 Rate Limiting

API menerapkan rate limiting untuk mencegah abuse:
- 100 requests per minute per IP
- 1000 requests per hour per user

## 📝 Error Response Format

```json
{
  "detail": "Error message description"
}
```

Untuk validation errors:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## 🔗 Interactive Documentation

Kunjungi `/docs` untuk dokumentasi interaktif Swagger UI atau `/redoc` untuk dokumentasi ReDoc.

## 💡 Tips Penggunaan

1. **Authentication**: Selalu sertakan JWT token di header Authorization
2. **File Upload**: Gunakan `multipart/form-data` untuk upload file
3. **Pagination**: Gunakan `skip` dan `limit` untuk pagination
4. **Search**: Kombinasikan multiple filters untuk hasil yang lebih akurat
5. **Access Control**: Cek status akses sebelum request download

---

*Dokumentasi ini di-generate berdasarkan kode API saat ini. Untuk perubahan terbaru, lihat `/docs` endpoint.*