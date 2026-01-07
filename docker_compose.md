# 🐳 Docker Setup Guide - Campus Archive Platform

## 📋 Prerequisites

Sebelum memulai, pastikan Anda sudah menginstall:

```bash
# Check Docker version
docker --version
# Required: Docker version 20.10+

# Check Docker Compose version
docker-compose --version
# Required: Docker Compose version 2.0+
```

## 📁 Struktur File yang Diperlukan

```
campus-archive/
├── docker-compose.yml          # ✅ Sudah dibuat
├── .env                        # ⚠️ Perlu dibuat dari .env.example
├── .env.example               # ✅ Sudah dibuat
│
├── nginx/
│   ├── nginx.conf             # ✅ Sudah dibuat
│   └── conf.d/
│       └── campus-archive.conf # ✅ Sudah dibuat
│
├── backend/
│   ├── Dockerfile             # ⚠️ Perlu dibuat
│   ├── requirements.txt       # ⚠️ Perlu ada
│   └── app/                   # ⚠️ Kode backend Anda
│
└── frontend/
    ├── dockerfile             # ⚠️ Perlu dibuat
    ├── package.json           # ⚠️ Perlu ada
    └── src/                   # ⚠️ Kode frontend Anda
```

---

## 🚀 Step-by-Step Setup

### Step 1: Buat Environment File

```bash
# Copy .env.example ke .env
cp .env.example .env

# Edit .env dengan editor favorit
nano .env  # atau: vim .env, code .env
```

**PENTING**: Update minimal settings berikut di `.env`:

```bash
# 1. Generate SECRET_KEY baru
SECRET_KEY=$(openssl rand -hex 32)

# 2. Ganti password database
POSTGRES_PASSWORD=your_strong_password_here_123456

# 3. Update domain (ganti yourdomain.com dengan domain Anda)
DOMAIN=campusarchive.ac.id
ALLOWED_ORIGINS=https://campusarchive.ac.id

# 4. Update API URL untuk frontend
VITE_API_URL=https://campusarchive.ac.id/api
```

### Step 2: Buat Dockerfile untuk Backend

Buat file `backend/Dockerfile`:

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Command akan di-override oleh docker-compose.yml
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 3: Buat Dockerfile untuk Frontend

Buat file `frontend/dockerfile`:

```dockerfile
# frontend/dockerfile
# Stage 1: Build React app
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build argument untuk API URL
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Build app
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy custom nginx config (optional)
# COPY nginx.conf /etc/nginx/nginx.conf

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

### Step 4: Buat Folder untuk Nginx

```bash
# Buat folder nginx configuration
mkdir -p nginx/conf.d
mkdir -p nginx/ssl

# Copy file konfigurasi yang sudah dibuat
# (nginx.conf dan campus-archive.conf sudah ada di artifacts di atas)
```

### Step 5: Validasi Setup

```bash
# Check apakah semua file ada
ls -la docker-compose.yml .env
ls -la backend/Dockerfile backend/requirements.txt
ls -la frontend/dockerfile frontend/package.json
ls -la nginx/nginx.conf nginx/conf.d/campus-archive.conf

# Validasi docker-compose syntax
docker-compose config
```

---

## 🔧 Development Mode (Local Testing)

### Start All Services

```bash
# Build dan start semua container
docker-compose up --build

# Atau jalankan di background
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# View logs untuk service tertentu
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Access Services

```
Frontend:  http://localhost:5173
Backend:   http://localhost:8000
API Docs:  http://localhost:8000/docs
Database:  localhost:5432
```

### Development Commands

```bash
# Restart specific service
docker-compose restart backend

# Rebuild specific service
docker-compose up -d --build backend

# Execute command inside container
docker-compose exec backend bash
docker-compose exec postgres psql -U archive_user -d campus_archive_db

# View container logs in real-time
docker-compose logs -f --tail=100

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ Hapus data!)
docker-compose down -v
```

---

## 🚀 Production Deployment

### Step 1: Setup VPS

```bash
# SSH ke VPS
ssh root@your-vps-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Create deploy user
adduser deploy
usermod -aG docker deploy
su - deploy
```

### Step 2: Clone Repository

```bash
# Clone project
cd /home/deploy
git clone https://github.com/yourusername/campus-archive.git
cd campus-archive

# Copy dan edit .env
cp .env.example .env
nano .env

# Update production settings:
# - ENVIRONMENT=production
# - DEBUG=False
# - Strong passwords
# - Real domain name
```

### Step 3: Setup SSL Certificate (Let's Encrypt)

```bash
# Install certbot
apt install certbot -y

# Stop nginx jika running
docker-compose stop nginx

# Generate certificate (ganti yourdomain.com)
certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email your-email@example.com \
  --agree-tos

# Certificates akan disimpan di:
# /etc/letsencrypt/live/yourdomain.com/

# Copy certificates ke project folder
mkdir -p nginx/ssl/live/yourdomain.com
cp /etc/letsencrypt/live/yourdomain.com/* nginx/ssl/live/yourdomain.com/

# Update nginx config dengan domain yang benar
nano nginx/conf.d/campus-archive.conf
# Ganti semua "yourdomain.com" dengan domain Anda
```

### Step 4: Start Production Services

```bash
# Build dan start
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Verify all containers healthy
docker-compose ps | grep Up
```

### Step 5: Verify Deployment

```bash
# Check HTTP redirect to HTTPS
curl -I http://yourdomain.com
# Should return 301 redirect

# Check HTTPS working
curl -I https://yourdomain.com
# Should return 200 OK

# Check API endpoint
curl https://yourdomain.com/api/health
# Should return JSON response

# Check SSL certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

---

## 🔄 Database Migrations

### Run Migrations

```bash
# Auto-run on container start (already configured in docker-compose.yml)
# Manual run:
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "Add new field"

# Rollback migration
docker-compose exec backend alembic downgrade -1

# Check migration status
docker-compose exec backend alembic current
```

---

## 💾 Backup & Restore

### Database Backup

```bash
# Create backup directory
mkdir -p /home/deploy/backups

# Manual backup
docker-compose exec -T postgres pg_dump -U archive_user campus_archive_db \
  > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup with compression
docker-compose exec -T postgres pg_dump -U archive_user campus_archive_db \
  | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Automated daily backup (cron)
crontab -e

# Add this line:
0 2 * * * cd /home/deploy/campus-archive && docker-compose exec -T postgres pg_dump -U archive_user campus_archive_db | gzip > /home/deploy/backups/backup_$(date +\%Y\%m\%d).sql.gz
```

### Database Restore

```bash
# Stop application
docker-compose stop backend frontend

# Restore from backup
gunzip < backup_20250106.sql.gz | \
  docker-compose exec -T postgres psql -U archive_user -d campus_archive_db

# Restart application
docker-compose start backend frontend
```

### File Uploads Backup

```bash
# Backup uploads directory
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/

# Restore uploads
tar -xzf uploads_backup_20250106.tar.gz
```

---

## 📊 Monitoring & Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f nginx

# Last 100 lines
docker-compose logs --tail=100

# Follow with timestamp
docker-compose logs -f -t

# Search logs
docker-compose logs backend | grep ERROR
```

### Container Stats

```bash
# Real-time resource usage
docker stats

# Check disk usage
docker system df

# Check specific container
docker stats campus_archive_backend
```

### Database Monitoring

```bash
# Connect to database
docker-compose exec postgres psql -U archive_user -d campus_archive_db

# Check connections
SELECT count(*) FROM pg_stat_activity;

# Check database size
SELECT pg_size_pretty(pg_database_size('campus_archive_db'));

# Check table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Check slow queries (if pg_stat_statements enabled)
SELECT 
    query,
    calls,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## 🔧 Troubleshooting

### Container Won't Start

```bash
# Check logs for error
docker-compose logs backend

# Check configuration
docker-compose config

# Rebuild from scratch
docker-compose down
docker-compose up --build
```

### Database Connection Error

```bash
# Check postgres is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Try connecting manually
docker-compose exec postgres psql -U archive_user -d campus_archive_db

# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL
```

### Out of Disk Space

```bash
# Check disk usage
df -h
du -sh /var/lib/docker

# Clean unused Docker resources
docker system prune -a
docker volume prune

# Clean old images
docker images | grep none | awk '{print $3}' | xargs docker rmi
```

### SSL Certificate Issues

```bash
# Check certificate expiry
certbot certificates

# Renew certificate
certbot renew

# Force renewal
certbot renew --force-renewal

# Update certificate in nginx
cp /etc/letsencrypt/live/yourdomain.com/* nginx/ssl/live/yourdomain.com/
docker-compose restart nginx
```

### Port Already in Use

```bash
# Check what's using port 80
sudo lsof -i :80

# Stop the conflicting service
sudo systemctl stop apache2  # atau service lain

# Or change port in docker-compose.yml
# ports:
#   - "8080:80"  # Use port 8080 instead
```

---

## 🔄 Update & Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Run migrations
docker-compose exec backend alembic upgrade head

# Check status
docker-compose ps
```

### Update Docker Images

```bash
# Pull latest base images
docker-compose pull

# Rebuild with latest images
docker-compose up -d --build
```

### Clean Old Data

```bash
# Remove old log files
find /var/log -name "*.log" -mtime +30 -delete

# Remove old backups
find /home/deploy/backups -name "*.sql.gz" -mtime +7 -delete

# Clean Docker system
docker system prune -f
```

---

## 📝 Cheat Sheet

```bash
# === START/STOP ===
docker-compose up -d              # Start all services
docker-compose down               # Stop all services
docker-compose restart            # Restart all services

# === BUILD ===
docker-compose build              # Build all images
docker-compose up --build         # Build and start

# === LOGS ===
docker-compose logs -f            # Follow all logs
docker-compose logs -f backend    # Follow backend logs

# === EXECUTE COMMANDS ===
docker-compose exec backend bash  # Enter backend container
docker-compose exec postgres psql # Enter database

# === STATUS ===
docker-compose ps                 # List containers
docker stats                      # Resource usage

# === CLEANUP ===
docker-compose down -v            # Stop and remove volumes
docker system prune -a            # Clean everything
```

---

## 🆘 Need Help?

Jika Anda mengalami masalah:

1. Check logs: `docker-compose logs -f`
2. Check .env file konfigurasi
3. Verify database connection
4. Check disk space: `df -h`
5. Review nginx error logs: `docker-compose logs nginx`

**Common Issues:**
- Database connection refused → Check postgres health
- 502 Bad Gateway → Backend container not running
- File upload fails → Check upload directory permissions
- SSL error → Verify certificate paths in nginx config