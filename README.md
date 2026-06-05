# CloudERP CRM/WMS Platform

A secure, scalable, cloud-ready ERP + CRM + WMS platform for a wholesale clothing
distributor, built for **BTEC Unit 6: Networking in the Cloud**. Django 5 + Django REST
Framework, PostgreSQL, Docker, GitHub Actions CI/CD, and an AWS-ready network design.

---

## Modules (all managed in the frontend — no Django admin required)

| Module | Features |
|--------|----------|
| **Authentication** | Login / logout, custom user with **RBAC** roles (Admin, Manager, Warehouse, Sales) |
| **CRM** | Customers, Leads (status pipeline), Sales Orders with line items + live total |
| **ERP** | Products, Categories, Suppliers, Purchase Orders, Employees |
| **WMS** | Warehouses, Inventory (+ reorder flag), Stock Movements (in/out), Shipments |
| **User management** | Create/edit users and assign roles (Admin only) |
| **Dashboard** | Role-aware statistics cards + Chart.js charts (orders-by-status, stock-by-warehouse) |
| **REST API** | `/api/{customers,orders,products,warehouses,inventory,users}/` with auth, permissions, pagination, filtering, search |

Every entity has full **create / read / update / delete** screens built with Django +
Bootstrap 5. Django's built-in admin is still available at `/admin/` for the Admin role,
but it is **not** part of the normal workflow — staff never get bounced into it.

## Role-based access (what each role sees)

The sidebar only shows modules a role can use, and the server enforces the same rules — so
users never hit a raw "403 Forbidden"; restricted areas simply aren't shown, and a direct
URL shows a friendly "access denied" page.

| Module | Admin | Manager | Sales | Warehouse |
|--------|:-----:|:-------:|:-----:|:---------:|
| CRM (customers/leads/orders) | ✅ | ✅ | ✅ | — |
| Products | ✅ | ✅ | view | view |
| ERP (suppliers/purchasing/employees/categories) | ✅ | ✅ | — | — |
| WMS (warehouses/inventory/stock/shipments) | ✅ | ✅ | — | ✅ |
| User management | ✅ | — | — | — |
| REST API link | ✅ | ✅ | — | — |
| Django admin | ✅ | — | — | — |

Access rules live in one file — `accounts/roles.py` — so adding a role or changing a
permission is a single edit.

---

## Tech stack

- **Backend:** Python 3.12, Django 5, Django REST Framework, django-filter
- **Frontend:** Django templates + Bootstrap 5 + Bootstrap Icons + Chart.js
- **Database:** PostgreSQL (SQLite fallback for zero-config local runs)
- **Server:** Gunicorn + WhiteNoise (static files)
- **Containers:** Docker + Docker Compose
- **CI/CD:** GitHub Actions (lint → security scan → tests → docker build)

---

## Quick start (local, no Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # leave POSTGRES_DB blank to use SQLite
python manage.py migrate
python manage.py seed_demo    # creates demo data + demo users
python manage.py runserver
```

Open http://127.0.0.1:8000/ and log in.

### Demo accounts (created by `seed_demo`)

| Username | Role | Password |
|----------|------|----------|
| `admin` | Administrator (superuser) | `ChangeMe123!` |
| `manager` | Manager | `ChangeMe123!` |
| `warehouse` | Warehouse Staff | `ChangeMe123!` |
| `sales` | Sales Staff | `ChangeMe123!` |

> Change these before any real deployment — they exist only for demonstration/screenshots.

---

## Run with Docker (PostgreSQL)

```bash
cp .env.example .env          # keep POSTGRES_* values
docker compose up --build
# in another shell, seed demo data:
docker compose exec web python manage.py seed_demo
```

App: http://localhost:8000/ — Postgres runs in its own container with a persistent volume.
The `entrypoint.sh` waits for the DB, runs migrations and `collectstatic` automatically.

---

## Environment variables

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Long random secret (required in production) |
| `DJANGO_DEBUG` | `True` for dev, `False` for production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated https origins (behind ALB) |
| `POSTGRES_DB/USER/PASSWORD/HOST/PORT` | DB connection (blank `POSTGRES_DB` → SQLite) |

No secrets are committed — `.env` is git-ignored and `.env.example` is the template.

---

## REST API

All endpoints require authentication (session or HTTP Basic). Examples:

```
GET    /api/customers/?search=acme&ordering=name
POST   /api/customers/            (Manager/Admin only)
GET    /api/orders/?status=CONFIRMED
GET    /api/inventory/?warehouse=1
GET    /api/users/                (Admin only)
```

Responses are paginated (`?page=2`, 10 per page). Browse interactively at `/api/`.

**Permission model** (`accounts/permissions.py`):
- `IsManagerOrReadOnly` — everyone reads; only Manager/Admin write (customers, products, warehouses).
- `IsAdminRole` — user management restricted to Admins.

---

## Testing

```bash
python manage.py test          # 10 tests: models, views, API auth/permissions, health
python manage.py check --deploy  # security configuration audit
```

### Performance testing (for criteria C.M3 / C.D2 / D.M4)

The brief requires evidence that the app scales under load. After deploying:

```bash
# Apache Bench example against the dashboard health endpoint
ab -n 5000 -c 100 https://erp.company.com/health/
```

Capture: requests/sec, mean latency, and the **Auto Scaling Group instance count** before
and after the spike (AWS console → EC2 → Auto Scaling). Discuss the results against the
single-server baseline in your report to justify the design (D.D3).

---

## AWS deployment readiness

The app is built to run unchanged on AWS:
- **EC2** instances in private subnets run the Docker image (behind the ALB).
- **RDS PostgreSQL** (Multi-AZ) replaces the local Postgres container — only env vars change.
- **Application Load Balancer** health-checks `/health/`.
- **Auto Scaling Group** scales the EC2 tier on CPU.
- **Route 53** maps the domain to the ALB.
- **VPC** isolation, security groups and NAT/Internet gateways per `docs/CLOUD_NETWORKING.md`.

Full network design, ASCII diagrams and the criteria mapping are in
[`docs/CLOUD_NETWORKING.md`](docs/CLOUD_NETWORKING.md).

---

## Project structure

```
cloud_erp/
├── config/            # settings, root urls, wsgi
├── accounts/          # custom User + roles + RBAC permissions + seed_demo command
├── core/              # shared abstract TimeStampedModel
├── crm/               # customers, leads, sales orders (+ web CRUD)
├── erp/               # products, categories, suppliers, purchasing, employees
├── wms/               # warehouses, inventory, stock movements, shipments
├── api/               # DRF serializers, viewsets, router
├── dashboard/         # dashboard view + /health/ endpoint
├── templates/         # base layout, login, dashboard, CRM pages
├── static/css/        # enterprise theme
├── docs/              # cloud networking documentation
├── .github/workflows/ # CI/CD pipeline
├── Dockerfile  docker-compose.yml  entrypoint.sh
├── requirements.txt  .env.example  .gitignore
└── manage.py
```

---

## Academic integrity note

This codebase is a working implementation you can run, screenshot and extend. The
**written report** (learning aims A–D: benefits/constraints, standards comparison,
justifications, test analysis) must be authored in your own words and supported by your
own load-test results. Be ready to explain any part of this project to your assessor.
