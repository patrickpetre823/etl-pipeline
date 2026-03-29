# ETL Pipeline with Airflow & Google Cloud

In this project I built an automated data pipeline, that ingests data from an public api, transforms it and stores it in a database.



---

## Tech Stack
| Technology              |  Purpose                                                               |
|-------------------------|------------------------------------------------------------------------|
| Apache Airflow          | Orchestrating the ETL pipeline.                                        |
| PostgreSQL              | Storing transformed data.                                              |
| Docker                  | Containerizing Airflow                                                 |
| Google Cloud Platform   |Hosting VMs and PostgreSQL instances.                                   |
| Python                  | Scripting for ETL logic.                                               |

---

## Data used

The data used for this project comes from tankeroenig API https://creativecommons.tankerkoenig.de/
There are several API-Methods, while I used Method 2 for this project giving me price information on all gasstations in a certain radius.

## API Response Structure
```json
{
  "ok": true,
  "license": "CC BY 4.0 - https://creativecommons.tankerkoenig.de",
  "data": "MTS-K",
  "status": "ok",
  "stations": [
    {
      "id": "474e5046-deaf-4f9b-9a32-9797b778f047",
      "name": "TOTAL BERLIN",
      "brand": "TOTAL",
      "street": "MARGARETE-SOMMER-STR.",
      "houseNumber": "2",
      "place": "BERLIN",
      "postCode": 10407,
      "lat": 52.53083,
      "lng": 13.440946,
      "dist": 1.1,
      "diesel": 1.109,
      "e5": 1.339,
      "e10": 1.319,
      "isOpen": true
    }
  ]
}
```

### Field Descriptions

| Field | Type | Description |
|---|---|---|
| `ok` | boolean | `true` if the request was successful |
| `license` | string | License information for the data |
| `data` | string | Data source identifier |
| `status` | string | Status of the response |
| `stations` | array | List of gas stations matching the query |

#### Station Object

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Unique identifier for the gas station |
| `name` | string | Name of the gas station |
| `brand` | string | Brand of the gas station |
| `street` | string | Street name |
| `houseNumber` | string | House number |
| `place` | string | City |
| `postCode` | integer | Postal code |
| `lat` | float | Latitude |
| `lng` | float | Longitude |
| `dist` | float | Distance to the search location in km |
| `diesel` | float | Diesel price in EUR |
| `e5` | float | E5 petrol price in EUR |
| `e10` | float | E10 petrol price in EUR |
| `isOpen` | boolean | `true` if the station is currently open |

## Pipeline Overview

The DAG extracts data from the API, transforms it into a structured DataFrame, and loads it into PostgreSQL.

**DataFrame columns:**
```
id, name, brand, street, place, lat, lng, dist,
diesel, e5, e10, isOpen, houseNumber, postCode,
retrieval_time, retrieval_date
```

- `retrieval_time` is stored in **Europe/Berlin** timezone
- Data transfer between tasks uses **Airflow XCom** (note: Airflow 2.0+ uses `context` instead of `kwargs`)

---

## Setup

### 1. Local Setup with Docker

1. Create project folders and set the Airflow UID
2. Download the official Docker Compose file via `curl`
3. Adjust the Compose file:
   - Set executor to `LocalExecutor` (remove CeleryWorker, Redis, and Worker services)
   - Remove Redis dependency
   - Set `AIRFLOW__CORE__LOAD_EXAMPLES=false`
   - Comment out the default `image:` line and point to a custom `Dockerfile` instead
4. Create a `Dockerfile` based on the [official Airflow docs](https://airflow.apache.org/docs/docker-stack/index.html)
   - Remove the pinned Airflow version from the Dockerfile
5. Create a `requirements.txt` for additional Python dependencies (e.g. `pytz`)
6. Remove the `triggerer` service from Compose
7. Add a `.gitignore` — make sure the API key is excluded

### 2. Google Cloud Migration

#### VM Setup

1. Create an **e2 instance** on GCP (Ubuntu, HTTPS enabled) — if memory/CPU is insufficient, scale up the instance type
2. Generate an SSH key locally:
```bash
   ssh-keygen -t rsa -f ~/.ssh/KEYNAME -C USERNAME
```
3. Add the public key to GCP and connect:
```bash
   ssh USERNAME@EXTERNAL_IP
```
4. Install Docker on the VM: [Docker install guide for Ubuntu](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)
5. Add the user to the Docker group:
```bash
   sudo usermod -aG docker $USER
```

#### Repository & Permissions

6. Clone the GitHub repository onto the VM
7. Fix file ownership if needed:
```bash
   sudo chown -R USERNAME:USERNAME /home/USERNAME/etl-pipeline/dags/
```
8. Configure Git:
```bash
   git config --global user.name "Your GitHub Display Name"
   git config --global user.email "your-github-email@example.com"
```
9. Generate an SSH key on the VM for GitHub access and add the public key to GitHub:
```bash
   ssh-keygen -t ed25519 -C "your-github-email@example.com"
```
10. Switch the remote URL from HTTPS to SSH:
```bash
    git remote set-url origin git@github.com:YOUR_USERNAME/etl-pipeline.git
```

#### VS Code Remote SSH

Generate a separate SSH key locally for VS Code Remote SSH access and add it to the GCP VM's authorized keys.

#### PostgreSQL on GCP

1. Create a **Cloud SQL instance** (PostgreSQL) and a database in GCP
2. Create a service account with the **Cloud SQL Client** role
3. Create a **VPC** and enable the **Service Networking API**
4. Enable **Private IP** for the Cloud SQL instance
5. Create a **Firewall rule** to allow connections to the database
6. Install `psql` on the VM and test the connection:
```bash
   psql -h DB_PRIVATE_IP -U DB_USER -d DB_NAME
```
## Local Data Migration

To perform data analysis locally and reduce cloud costs, the database was migrated from GCP Cloud SQL to a local PostgreSQL instance running in Docker.

### Steps

1. Install PostgreSQL client (v18 to match the GCP instance):
```bash
   sudo sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt noble-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
   curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo tee /etc/apt/trusted.gpg.d/postgresql.asc
   sudo apt update
   sudo apt install -y postgresql-client-18
```

2. Dump the database directly from GCP Cloud SQL (public IP):
```bash
   pg_dump -h PUBLIC_SQL_IP -U postgres -d gasstation-db -f ~/dump.sql
```

3. Start a local PostgreSQL container:
```bash
   docker run --name pg-local \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=your_password \
     -e POSTGRES_DB=gasstation-db \
     -p 5432:5432 \
     -d postgres:18
```

4. Load the dump into the local container:
```bash
   docker exec -i pg-local psql -U postgres -d gasstation-db < ~/dump.sql
```

> The `dump.sql` file is stored locally in `data/` but excluded from version control via `.gitignore`.
---

## Resources

- [Tankerkönig API Docs](https://creativecommons.tankerkoenig.de/)
- [Apache Airflow on GCP VM – Full Guide](https://medium.com/@kwattrapuranjay/apache-airflow-on-google-cloud-vm-a-complete-guide-with-custom-mysql-database-redis-caching-and-c00d1fd86cf2)
- [Docker Install on Ubuntu](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)



