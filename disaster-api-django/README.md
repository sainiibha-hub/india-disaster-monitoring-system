# India Disaster Monitoring -- Django REST API

A GET-only, read-only REST API built with Django + Django REST Framework
that serves data from the **same MySQL database** your existing
Flask/Python monitoring system (`india-disaster-monitoring/`) already
creates and fills. This project does not collect any data itself -- run
`python main.py --run` (or `scheduler.py`) in the other project as usual;
this API just reads what's already in the database and returns JSON.

## Why this is safe to point at an existing database

Every model in `monitoring/models.py` has `managed = False` and an exact
`db_table` name matching the existing schema. Django will **never**
create, alter, or drop those tables -- it only ever runs `SELECT`.

## Setup

```bash
cd disaster-api-django
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: use the SAME DB_HOST/DB_USER/DB_PASSWORD/DB_NAME as your
# existing india-disaster-monitoring/.env file
```

> **Why PyMySQL instead of mysqlclient?** Django's default MySQL backend
> wants the `mysqlclient` package, which needs a C compiler to install on
> Windows. `PyMySQL` is pure Python and just works with `pip install`.
> `disaster_api_project/__init__.py` has two lines that make PyMySQL act
> as a drop-in replacement, so the rest of Django is unaware of the swap.

```bash
python manage.py migrate    # sets up Django's own internal tables only
                             # (auth, contenttypes) -- never touches your
                             # monitoring tables, since those are managed=False
python manage.py runserver
```

Open **http://127.0.0.1:8000/api/summary/** -- you should see JSON.

## Endpoints (all GET)

| Endpoint | Description |
|---|---|
| `GET /api/states/` | All states |
| `GET /api/districts/` | All districts, with their state name |
| `GET /api/rainfall/latest/` | Most recent rainfall reading per district |
| `GET /api/rainfall/trend/?days=30` | Daily avg/peak rainfall, for charts |
| `GET /api/rainfall/top-states/?date=YYYY-MM-DD` | Highest rainfall states (defaults to today) |
| `GET /api/floods/` | Most recent flood alerts |
| `GET /api/earthquakes/?days=30&min_magnitude=5.0` | Earthquakes (defaults match the spec: 30 days, M≥5.0) |
| `GET /api/cyclones/` | Most recent cyclone advisories |
| `GET /api/reports/` or `?date=YYYY-MM-DD` | Daily reports |
| `GET /api/summary/` | Today's headline numbers (same shape as the Flask dashboard's `/api/summary`) |

Example:
```bash
curl http://127.0.0.1:8000/api/earthquakes/
curl "http://127.0.0.1:8000/api/rainfall/trend/?days=7"
```

## Browsable API

Since `rest_framework.renderers.BrowsableAPIRenderer` is enabled, you can
also just open any endpoint URL directly in a browser (e.g.
`http://127.0.0.1:8000/api/floods/`) and get a nicely formatted, clickable
HTML view of the same JSON -- handy while testing.

## This API is intentionally read-only

No POST/PUT/PATCH/DELETE endpoints are defined, matching the request for
a GET-only API. If you later want write access (e.g. to let a mobile app
submit a new rainfall reading), add `ModelViewSet`s + a router instead of
`ListAPIView`/`APIView`, and swap `AllowAny` for a real permission class
in `settings.py` first.

## Project structure

```
disaster-api-django/
├── manage.py
├── requirements.txt
├── .env.example
├── disaster_api_project/
│   ├── __init__.py        # PyMySQL shim
│   ├── settings.py        # DB config (same DB as the Flask project)
│   ├── urls.py
│   └── wsgi.py
└── monitoring/
    ├── models.py          # managed=False models mirroring the existing tables
    ├── serializers.py
    ├── views.py           # all GET endpoints
    ├── urls.py
    ├── apps.py
    └── migrations/        # empty -- nothing to migrate (managed=False)
```
