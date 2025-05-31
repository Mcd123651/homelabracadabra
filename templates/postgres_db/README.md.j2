# PostgreSQL Docker Setup (Homelab)

This folder contains a Dockerized PostgreSQL 14.1 instance configured for homelab usage and local service onboarding.

## 📦 Setup

Build and start the container:

```bash
docker compose up -d
```

The database will be available at:

- **Host**: `localhost`
- **Port**: `5432`
- **User**: `docker_user`
- **Password**: `docker_user`

Data is persisted in `./dbdata`.

---

## 🛠️ Common Commands

### 🔄 Restart the DB container

```bash
docker compose restart
```

### 🧑‍💻 Connect to `psql` CLI

```bash
docker exec -it postgres_db psql -U docker_user
```

Or connect to a specific database:

```bash
docker exec -it postgres_db psql -U docker_user -d homelab
```

---

## 🆕 Create New Databases

### 🏗️ Create additional service databases:

```bash
docker exec -it postgres_db psql -U docker_user -d postgres -c "CREATE DATABASE wikijs;"
docker exec -it postgres_db psql -U docker_user -d postgres -c "CREATE DATABASE homeassistant;"
```

---

## 💾 Backup & Restore Examples

### Backup

Add this `backup` service snippet to your `docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:14.1-alpine
    container_name: postgres_db
    environment:
      POSTGRES_DB: homelab
      POSTGRES_USER: docker_user
      POSTGRES_PASSWORD: docker_user
    volumes:
      - ./dbdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  backup:
    image: postgres:14.1-alpine
    container_name: postgres_backup
    depends_on:
      - db
    entrypoint: ["/bin/sh", "-c"]
    command: >
      pg_dump -h db -U docker_user homelab > /backups/homelab_backup_$(date +%Y%m%d_%H%M%S).sql
    environment:
      PGPASSWORD: docker_user
    volumes:
      - ./backups:/backups
```

Run a manual backup with:

```bash
docker compose run --rm backup
```

This will create a timestamped SQL dump file in the `./backups` folder.

---

### Restore

To restore a backup into a database (e.g. `homelab`), first make sure the database exists:

```bash
docker exec -it postgres_db psql -U docker_user -d postgres -c "CREATE DATABASE homelab;"
```

Then restore from the backup SQL file:

```bash
cat ./backups/homelab_backup_YYYYMMDD_HHMMSS.sql | docker exec -i postgres_db psql -U docker_user -d homelab
```

Replace `homelab_backup_YYYYMMDD_HHMMSS.sql` with your actual backup filename.

---

## 🧹 Stop and Remove Everything

**WARNING: This deletes all database data!**

```bash
docker compose down -v
rm -rf ./dbdata
```

---

## 🧰 Optional Enhancements

- Use `init-multiple-dbs.sql` for first-time initialization.
- Use `pgAdmin` or `DBeaver` for GUI access.
- Automate backups with scheduled tasks (cron jobs or external schedulers).
- Create dedicated users/roles per service.

---

## 📁 Directory Structure

```
postgres/
├── docker-compose.yml
├── init-multiple-dbs.sql   # Optional, only runs on first container init
├── dbdata/                 # Persistent Postgres data volume
├── backups/                # Backup output folder
└── README.md
```

---
