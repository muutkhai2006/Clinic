# ClinicCare - De 8: He thong Quan ly Phong kham / Benh vien

Bo bai thuc hanh cho hoc phan **Trien khai va Quan tri He thong Phan mem**.

## 1. Muc tieu

Website quan ly 3 nhom nghiep vu:

- Benh nhan: them, xem, sua, xoa.
- Bac si: them, xem, sua, xoa.
- Lich kham: dat lich, sua, xoa; rang buoc khong trung bac si + ngay + gio.

Stack trien khai:

- Flask + Gunicorn
- PostgreSQL + pgAdmin
- Nginx reverse proxy
- Prometheus + Grafana
- postgres_exporter + nginx-prometheus-exporter + cAdvisor + Blackbox Exporter
- Loki + Promtail + LogQL
- Docker Compose

> Luu y 2026: Promtail da EOL, nhung bo bai nay van dung Promtail vi de/rubric hoc phan yeu cau. Neu trien khai moi ngoai bai thuc hanh, nen chuyen sang Grafana Alloy.

---

# 2. Yeu cau may

Tren Windows:

1. Cai Docker Desktop.
2. Docker Desktop phai o che do **Linux containers / WSL2 backend**.
3. Kiem tra trong PowerShell:

```powershell
docker --version
docker compose version
```

Nen co Git de day bai len GitHub:

```powershell
git --version
```

Cac cong can trong:

| Dich vu | URL | Cong |
|---|---|---:|
| Website qua Nginx | http://localhost:8080 | 8080 |
| pgAdmin | http://localhost:8082 | 8082 |
| Grafana | http://localhost:3000 | 3000 |
| Prometheus | http://localhost:9090 | 9090 |

Neu bi trung cong, chay:

```powershell
netstat -ano | findstr :8080
netstat -ano | findstr :8082
netstat -ano | findstr :3000
netstat -ano | findstr :9090
```

---

# 3. Buoc 1 - Chuan bi .env

Trong thu muc project:

```powershell
Copy-Item .env.example .env
notepad .env
```

Doi tat ca gia tri co `ChangeMe` thanh mat khau rieng. Vi du mat khau nen >= 12 ky tu, co chu hoa, chu thuong, so va ky tu dac biet.

**Khong commit `.env` len GitHub.** File `.gitignore` da loai `.env`.

Kiem tra:

```powershell
git check-ignore .env
```

Neu hien `.env` la dung.

---

# 4. Buoc 2 - Build va khoi dong toan bo he thong

Cach nhanh: chay `CHAY_HE_THONG.bat`.

Hoac PowerShell:

```powershell
docker compose up -d --build
docker compose ps
```

Tat ca container quan trong nen o trang thai `Up`/`Running`; app va postgres co the co them `healthy` sau vai chuc giay.

Neu dich vu chua on:

```powershell
docker compose ps -a
docker compose logs --tail=100
docker compose logs --tail=100 app postgres nginx
```

**Anh minh chung nen chup:** `docker compose ps` hien danh sach dich vu dang chay.

---

# 5. Buoc 3 - Kiem tra Website quan ly phong kham

Mo:

- http://localhost:8080

Trang chu co cac the thong ke Benh nhan, Bac si, Tong lich kham, Lich hom nay.

## 5.1 CRUD Benh nhan

Mo `Benh nhan` va thu:

1. Them `BN004`.
2. Xem dong moi trong danh sach.
3. Bam `Sua`, thay doi so dien thoai/dia chi.
4. Xoa mot ban ghi thu nghiem.

## 5.2 CRUD Bac si

Mo `Bac si` va thu them/sua/xoa bac si.

## 5.3 CRUD Lich kham

Mo `Lich kham`:

1. Chon benh nhan.
2. Chon bac si.
3. Chon ngay/gio.
4. Nhap ly do kham.
5. Luu.

He thong co rang buoc `doctor_id + appointment_date + appointment_time` khong duoc trung.

**Anh minh chung nen chup:** trang chu, CRUD benh nhan, CRUD bac si, CRUD lich kham.

---

# 6. Buoc 4 - Kiem tra PostgreSQL bang pgAdmin

Mo:

- http://localhost:8082

Dang nhap bang `PGADMIN_DEFAULT_EMAIL` va `PGADMIN_DEFAULT_PASSWORD` trong `.env`.

Trong pgAdmin chon **Add New Server**:

### General

- Name: `Clinic PostgreSQL`

### Connection

- Host name/address: `postgres`
- Port: `5432`
- Maintenance database: gia tri `POSTGRES_DB` (mac dinh `clinic_db`)
- Username: gia tri `POSTGRES_USER` (mac dinh `clinic_app`)
- Password: `POSTGRES_PASSWORD`
- Save password: On (chi de demo local)

Sau khi ket noi, vao:

`Servers -> Clinic PostgreSQL -> Databases -> clinic_db -> Schemas -> public -> Tables`

Can thay 3 bang:

- `patients`
- `doctors`
- `appointments`

Co the kiem tra bang Terminal:

```powershell
docker compose exec postgres psql -U clinic_app -d clinic_db -c "\dt"
docker compose exec postgres psql -U clinic_app -d clinic_db -c "SELECT count(*) FROM patients;"
docker compose exec postgres psql -U clinic_app -d clinic_db -c "SELECT count(*) FROM doctors;"
docker compose exec postgres psql -U clinic_app -d clinic_db -c "SELECT count(*) FROM appointments;"
```

Neu da doi `POSTGRES_USER`/`POSTGRES_DB`, thay gia tri cho dung.

**Anh minh chung nen chup:** pgAdmin hien 3 bang nghiep vu va du lieu trong mot bang.

---

# 7. Buoc 5 - Chung minh Nginx Reverse Proxy

Ung dung Flask **khong publish cong 8000 ra host**. Nguoi dung chi truy cap web qua Nginx port 8080.

Kiem tra container app khong co host port:

```powershell
docker compose ps app nginx
```

Kiem tra Nginx config:

```powershell
docker compose exec nginx nginx -t
```

Kiem tra security headers:

```powershell
curl.exe -I http://localhost:8080/
```

Can thay cac header nhu:

- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: ...`

Nginx Exporter doc noi bo doc endpoint:

- `http://nginx:8081/stub_status`

Cong 8081 **khong publish ra host**.

**Anh minh chung nen chup:** `nginx -t` thanh cong va `curl -I` co security headers.

---

# 8. Buoc 6 - Prometheus + Grafana

## 8.1 Prometheus Targets

Mo:

- http://localhost:9090/targets

Can co cac job:

- `prometheus`
- `containers`
- `postgres`
- `nginx`
- `website`

Muc tieu: tat ca `UP`.

Neu `containers` DOWN tren Windows Docker Desktop, dam bao dang dung Linux containers + WSL2 backend. cAdvisor can quyen doc tai nguyen Docker nen duoc cau hinh `privileged: true` chi rieng dich vu giam sat nay.

## 8.2 PromQL de demo

Vao Prometheus -> Query va chay:

```promql
up
```

```promql
probe_success{job="website"}
```

```promql
pg_up
```

```promql
nginx_http_requests_total
```

```promql
sum(pg_stat_activity_count)
```

```promql
sum by (name) (rate(container_cpu_usage_seconds_total{name!=""}[5m]))
```

```promql
sum by (name) (container_memory_working_set_bytes{name!=""})
```

> Neu cAdvisor cua may ban khong co label `name`, mo Prometheus query `container_cpu_usage_seconds_total` de xem label thuc te. Co the thay `id` va chuyen truy van sang `sum by (id) (...)` giong cach xu ly trong bao cao mau.

## 8.3 Grafana

Mo:

- http://localhost:3000

Dang nhap bang `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD` trong `.env`.

Datasource Prometheus va Loki da duoc provision tu dong.

Vao:

`Dashboards -> ClinicCare -> ClinicCare | Website - Container - PostgreSQL - Nginx`

Dashboard co san cac panel:

- Website UP
- PostgreSQL UP
- Nginx HTTP Requests
- PostgreSQL Active Connections
- Container CPU
- Container RAM

Neu CPU/RAM `No data`, dung Query Inspector/Prometheus de kiem tra label cAdvisor va sua `grafana/dashboards/clinic-overview.json`.

**Anh minh chung nen chup:** trang Prometheus Targets va dashboard Grafana co data.

---

# 9. Buoc 7 - Loki + Promtail + LogQL

## 9.1 Kiem tra Loki/Promtail

```powershell
docker compose logs --tail=50 loki promtail
```

Tao them request web de sinh access log:

```powershell
1..30 | ForEach-Object { Invoke-WebRequest http://localhost:8080/ -UseBasicParsing | Out-Null }
```

Kiem tra log trong Nginx:

```powershell
docker compose exec nginx sh -c "tail -n 10 /var/log/nginx/access.log"
```

## 9.2 Chay 3 truy van LogQL bat buoc

Grafana -> Explore -> chon datasource `Loki`.

### Query 1 - Toan bo log Nginx

```logql
{job="nginx"}
```

### Query 2 - Loc HTTP GET

```logql
{job="nginx",logtype="access"} |= "GET"
```

### Query 3 - Dem request trong 5 phut

```logql
sum(count_over_time({job="nginx",logtype="access"}[5m]))
```

Co the them Query 4 de dep bai:

```logql
{job="nginx",logtype="access"} |~ " 4[0-9]{2} "
```

**Anh minh chung nen chup:** ket qua cua tung query; Query 3 chuyen visualization sang Time series.

---

# 10. Buoc 8 - Hardening / Bao mat

Bai nay co nhieu hon 4 bien phap de de chung minh:

## 10.1 Secrets khong len Git

- `.env` nam trong `.gitignore`.

```powershell
git check-ignore .env
```

## 10.2 PostgreSQL khong publish port 5432

```powershell
docker compose ps postgres
```

Cot `PORTS` khong co `0.0.0.0:5432->5432`.

## 10.3 Database network la internal

```powershell
docker network ls
```

Tim network co duoi `_database_net`, sau do:

```powershell
docker network inspect TEN_PROJECT_database_net
```

Can thay `"Internal": true`.

## 10.4 App chay non-root

```powershell
docker compose exec app id
```

Can thay UID 10001 thay vi root (UID 0).

## 10.5 App va Nginx read-only + drop capabilities + no-new-privileges

```powershell
docker inspect (docker compose ps -q app) --format '{{json .HostConfig.ReadonlyRootfs}}'
docker inspect (docker compose ps -q app) --format '{{json .HostConfig.CapDrop}}'
docker inspect (docker compose ps -q app) --format '{{json .HostConfig.SecurityOpt}}'
```

## 10.6 Security headers Nginx

```powershell
curl.exe -I http://localhost:8080/
```

**Anh minh chung nen chup:** 1 anh ghep cac lenh tren hoac 2 anh ro rang.

---

# 11. GitHub - Lam dung 3 moc commit de cham diem

Tao repository GitHub theo ma sinh vien neu giang vien yeu cau.

Khoi tao:

```powershell
git init
git branch -M main
git add .
git commit -m "Commit 1: Flask PostgreSQL pgAdmin Nginx reverse proxy"
```

Sau khi dam bao phan app + DB + Nginx chay on, day len GitHub.

Moc commit nen the hien nhu sau:

### Commit 1

```text
Commit 1: Flask PostgreSQL pgAdmin Nginx reverse proxy
```

Noi dung: website CRUD + PostgreSQL + pgAdmin + Nginx.

### Commit 2

Sau khi hoan thien Prometheus/Grafana:

```powershell
git add .
git commit -m "Commit 2: Prometheus Grafana monitoring dashboard"
```

### Commit 3

Sau khi hoan thien Loki/Promtail + hardening + README:

```powershell
git add .
git commit -m "Commit 3: Loki Promtail LogQL hardening documentation"
```

Kiem tra:

```powershell
git log --oneline --decorate -10
```

**Khong tao hash gia. Bao cao phai dan hash commit thuc te sau khi ban push.**

---

# 12. Checklist anh can chup de dua vao bao cao

1. `docker compose ps` - cac container.
2. Trang chu ClinicCare.
3. CRUD Benh nhan.
4. CRUD Bac si.
5. CRUD Lich kham.
6. pgAdmin - 3 bang va du lieu.
7. `nginx -t` + `curl -I` security headers.
8. Prometheus Targets tat ca UP.
9. Grafana dashboard co data.
10. LogQL `{job="nginx"}`.
11. LogQL GET.
12. LogQL count_over_time 5m.
13. Hardening: `.env` ignored, DB internal, app non-root, postgres khong public 5432.
14. GitHub repository + `git log --oneline` co 3 moc commit.

---

# 13. Bang kiem thu truoc khi nop

| STT | Ca kiem thu | Dat khi |
|---:|---|---|
| 1 | Trang chu | Mo duoc http://localhost:8080 |
| 2 | CRUD benh nhan | Them/sua/xoa thanh cong |
| 3 | CRUD bac si | Them/sua/xoa thanh cong |
| 4 | CRUD lich kham | Them/sua/xoa thanh cong |
| 5 | PostgreSQL/pgAdmin | Xem duoc 3 bang |
| 6 | Nginx | nginx -t OK, web qua 8080, co headers |
| 7 | Prometheus | Targets UP |
| 8 | Grafana | Co metrics website/Nginx/Postgres/container |
| 9 | Loki | 3 LogQL co ket qua |
| 10 | Hardening | It nhat 4 bien phap co minh chung |
| 11 | GitHub | README + source/config + 3 commit co y nghia |

---

# 14. Xu ly loi nhanh

## Port is already allocated

Tim tien trinh/dich vu dang chiem cong hoac doi port phia host trong `docker-compose.yml`.

## `app` restart lien tuc

```powershell
docker compose logs --tail=150 app postgres
```

Thuong do sai `POSTGRES_PASSWORD` hoac `.env` bi sua sau khi volume PostgreSQL da duoc tao. Neu day chi la bai demo va chap nhan xoa data:

```powershell
docker compose down -v
docker compose up -d --build
```

## pgAdmin khong ket noi DB

Host trong pgAdmin phai la `postgres`, **khong phai localhost**.

## Prometheus postgres target UP nhung `pg_up=0`

Kiem tra:

```powershell
docker compose logs --tail=100 postgres-exporter
```

Va kiem tra lai user/password/database trong `.env`.

## Loki khong co log

```powershell
docker compose exec nginx sh -c "ls -l /var/log/nginx && tail -n 20 /var/log/nginx/access.log"
docker compose logs --tail=100 promtail loki
```

Sau do vao Grafana Explore, chon dung datasource `Loki` va time range `Last 15 minutes` hoac `Last 1 hour`.

---

# 15. Lenh dung va reset

Dung, giu du lieu:

```powershell
docker compose down
```

Chay lai:

```powershell
docker compose up -d
```

Xoa ca volume de lam lai tu dau (MAT DATA):

```powershell
docker compose down -v
```


## Khoi tao file log Nginx (bo sung)

Dich vu `log-init` chay mot lan de tao hai file `access.log` va `error.log` trong named volume `nginx_logs`.
Day la buoc can thiet vi Nginx trong bo bai chay quyen han che, trong khi Promtail can doc duoc file log thuc te.
`log-init` se ket thuc voi status `Exited (0)` va do **khong phai loi**. Nginx phu thuoc vao viec khoi tao nay.
Khi `docker compose ps -a`, `log-init` la `Exited (0)` la binh thuong.

Chu y: Day la mo hinh demo hoc phan, KHONG su dung du lieu benh nhan that.
Website chua co dang nhap, phan quyen, ma hoa TLS hay quan ly ho so y te du tieu chuan van hanh that.
Khong publish he thong cong khai ra Internet. PostgreSQL chua co backup tu dong.

### Neu LogQL khong co du lieu

```powershell
docker compose logs --tail=80 nginx promtail loki
docker compose exec nginx sh -c 'ls -l /var/log/nginx && tail -n 10 /var/log/nginx/access.log'
```

Mo website / tai lai vai lan va truy van `{job="nginx"}` trong Grafana Explore.
