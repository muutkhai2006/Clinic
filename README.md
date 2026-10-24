# ClinicCare - Hệ thống quản lý phòng khám

Đây là bài thực hành môn **Triển khai và Quản trị Hệ thống Phần mềm**.

Đề tài thực hiện là **Hệ thống quản lý phòng khám / bệnh viện**.

## 1. Chức năng hệ thống

Hệ thống dùng để quản lý thông tin bệnh nhân, bác sĩ và lịch khám.

Người dùng có thể thêm, xem, sửa và xóa thông tin bệnh nhân.

Phần bác sĩ cho phép quản lý mã bác sĩ, họ tên, chuyên khoa, số điện thoại và phòng khám.

Phần lịch khám dùng để tạo và quản lý lịch khám giữa bệnh nhân và bác sĩ. Hệ thống có kiểm tra để hạn chế việc một bác sĩ bị đặt trùng cùng ngày và cùng giờ.

## 2. Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Ứng dụng web | Python Flask |
| Web Server | Gunicorn |
| Cơ sở dữ liệu | PostgreSQL 17 |
| Quản trị CSDL | pgAdmin 4 |
| Reverse Proxy | Nginx |
| Triển khai | Docker, Docker Compose |
| Giám sát | Prometheus |
| Dashboard | Grafana |
| Container Metrics | cAdvisor |
| Website Monitoring | Blackbox Exporter |
| PostgreSQL Metrics | PostgreSQL Exporter |
| Nginx Metrics | Nginx Exporter |
| Logging | Loki, Promtail |
| Quản lý mã nguồn | GitHub |

## 3. Môi trường triển khai

Hệ thống được triển khai trên Ubuntu Linux.

Docker Engine và Docker Compose được sử dụng để chạy toàn bộ các dịch vụ.

Kiểm tra Docker bằng các lệnh:

```bash
docker --version
docker compose version
docker ps
```

## 4. Chuẩn bị project

Clone project từ GitHub:

```bash
git clone git@github.com:muutkhai2006/Clinic.git
cd Clinic
```

Tạo file `.env` từ file mẫu:

```bash
cp .env.example .env
```

Mở file cấu hình:

```bash
nano .env
```

Ví dụ cấu hình:

```env
POSTGRES_DB=clinic_db
POSTGRES_USER=clinic_app
POSTGRES_PASSWORD=CHANGE_ME

PGADMIN_DEFAULT_EMAIL=admin@clinic.com
PGADMIN_DEFAULT_PASSWORD=CHANGE_ME

SECRET_KEY=CHANGE_ME

GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=CHANGE_ME
```

File `.env` chứa mật khẩu nên không được đưa lên GitHub.

## 5. Chạy hệ thống

Kiểm tra cấu hình Docker Compose:

```bash
docker compose config --quiet
```

Build và chạy hệ thống:

```bash
docker compose up -d --build
```

Kiểm tra trạng thái:

```bash
docker compose ps -a
```

Hệ thống gồm các service chính là `app`, `postgres`, `pgadmin`, `nginx`, `prometheus`, `grafana`, `loki`, `promtail`, `postgres-exporter`, `nginx-exporter`, `cadvisor` và `blackbox`.

Hai container `log-init` và `loki-init` chỉ thực hiện công việc khởi tạo nên có thể hiển thị trạng thái `Exited (0)` sau khi chạy xong.

## 6. Địa chỉ truy cập

Lấy địa chỉ IP Ubuntu:

```bash
hostname -I
```

| Dịch vụ | Địa chỉ |
|---|---|
| Website ClinicCare | `http://IP_UBUNTU:8080` |
| pgAdmin | `http://IP_UBUNTU:8082` |
| Grafana | `http://IP_UBUNTU:3000` |
| Prometheus | `http://IP_UBUNTU:9090` |
| Prometheus Targets | `http://IP_UBUNTU:9090/targets` |

## 7. PostgreSQL và pgAdmin

Khi thêm server PostgreSQL trong pgAdmin sử dụng thông tin:

```text
Host: postgres
Port: 5432
Database: clinic_db
Username: clinic_app
Password: lấy trong file .env
```

Cơ sở dữ liệu có ba bảng nghiệp vụ chính:

```text
patients
doctors
appointments
```

## 8. Nginx Reverse Proxy

Nginx được sử dụng làm reverse proxy cho website.

Ứng dụng Flask chạy ở cổng nội bộ `8000` nhưng không mở trực tiếp ra bên ngoài. Người dùng truy cập website thông qua Nginx ở cổng `8080`.

Kiểm tra:

```bash
curl -I http://localhost:8080
```

Nginx được cấu hình thêm các security header:

```text
X-Frame-Options
X-Content-Type-Options
Referrer-Policy
Permissions-Policy
```

## 9. Prometheus và Grafana

Prometheus được dùng để thu thập thông số của website, PostgreSQL, Nginx và các container.

Một số câu truy vấn PromQL đã sử dụng:

```promql
up
```

```promql
pg_up
```

```promql
probe_success{job="website"}
```

```promql
nginx_http_requests_total
```

```promql
container_memory_working_set_bytes
```

Grafana được sử dụng để hiển thị dữ liệu giám sát dưới dạng dashboard.

Dashboard chính:

```text
ClinicCare | Website - Container - PostgreSQL - Nginx
```

Dashboard theo dõi trạng thái website, PostgreSQL, số request của Nginx, kết nối PostgreSQL, CPU và RAM của các container.

## 10. Loki và Promtail

Promtail có nhiệm vụ đọc log của Nginx và gửi dữ liệu sang Loki.

Trong Grafana có thể vào:

```text
Explore -> Loki
```

Truy vấn toàn bộ log Nginx:

```logql
{job="nginx"}
```

Truy vấn access log có request GET:

```logql
{job="nginx",logtype="access"} |= "GET"
```

Thống kê số request trong 5 phút:

```logql
sum(count_over_time({job="nginx",logtype="access"}[5m]))
```

## 11. Hardening

File `.env` được đưa vào `.gitignore` để không đẩy mật khẩu lên GitHub.

Kiểm tra:

```bash
git check-ignore .env
```

PostgreSQL không publish cổng `5432` trực tiếp ra ngoài host.

Mạng `database_net` được cấu hình ở chế độ internal.

Kiểm tra:

```bash
docker network inspect clinic-deployment_database_net --format '{{.Internal}}'
```

Container ứng dụng chạy bằng user riêng thay vì root.

Kiểm tra:

```bash
docker compose exec app id
```

Một số container được cấu hình thêm `read_only`, `cap_drop: ALL` và `no-new-privileges`.

Nginx cũng được cấu hình các security header để tăng mức độ an toàn khi truy cập website.

## 12. Kiểm tra khi có lỗi

Kiểm tra trạng thái tất cả container:

```bash
docker compose ps -a
```

Xem log của một dịch vụ:

```bash
docker compose logs --tail=100 TEN_SERVICE
```

Ví dụ:

```bash
docker compose logs --tail=100 nginx
docker compose logs --tail=100 postgres
docker compose logs --tail=100 loki
```

## 13. Dừng và chạy lại hệ thống

Dừng hệ thống:

```bash
docker compose down
```

Chạy lại hệ thống:

```bash
docker compose up -d
```

Không sử dụng:

```bash
docker compose down -v
```

nếu vẫn muốn giữ dữ liệu trong các volume.

## 14. GitHub

Repository:

```text
https://github.com/muutkhai2006/Clinic
```

Quá trình thực hiện được chia thành các commit tương ứng với từng phần triển khai.

Commit đầu thực hiện website, PostgreSQL, pgAdmin và Nginx.

Commit tiếp theo bổ sung Prometheus, Grafana và hệ thống monitoring.

Commit sau bổ sung Loki, Promtail và truy vấn LogQL.

Các commit sau dùng để sửa lỗi quyền volume Loki trên Ubuntu và cập nhật lại tài liệu triển khai.

