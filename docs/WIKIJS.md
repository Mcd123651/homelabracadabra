# 📦 PostgreSQL Backup & Restore (Docker): `wikijs` Database

This guide explains how to back up and restore the `wikijs` PostgreSQL database using a Docker container.

---

## 🗃️ Backup the `wikijs` Database

### 1. Find the Running PostgreSQL Container

```bash
docker ps
```

Example output:

```
CONTAINER ID   IMAGE                  NAMES
32199f50067d   postgres:14.1-alpine   docker-db-1
```

### 2. Run `pg_dump` Inside the Container

- **Plain SQL format**:

```bash
docker exec -t docker-db-1 pg_dump -U docker_user -d wikijs > wikijs_backup.sql
```

---

## 🚚 Restore the Backup

- **Plain SQL format**:

```bash
docker exec -i postgres-db psql -U docker_user -d wikijs < wikijs_backup.sql
```
