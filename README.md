# 🧙‍♂️ homelabracadabra

> *Because it's magic when it works.*

**homelabracadabra** is a magical collection of Infrastructure as Code (IaC) for conjuring up self-hosted services, virtual machines, containers, and automations.

Built with **Proxmox**, **Ansible**, **Terraform**, and **Docker**, this repo powers my homelab—but it’s designed to be **adaptable for others** too. Hardware-agnostic configurations, templated provisioning, and modular service definitions mean *you* can fork this project and shape it to your own wizardry.

Whether you’re running on a Raspberry Pi, a rackmount server, or just dreaming of your future setup, these scripts can be customized to suit your network, VM layout, and service stack.

Let’s automate some magic.

---

## 🏠 Homelab Overview

### 🧠 Controller: Raspberry Pi 4
- Runs Git (this repo)
- Executes Terraform and Ansible for provisioning and orchestration
- Minimal control plane that stays online even during server reboots
- Orchestration

### 🎞️ Media Server: Windows PC
- Hosts Plex, Sonarr, Radarr, and Unpackerr
- 48TB storage pool for media
- 16GB VRAM (used for Ollama / local AI inference)
- Will continue to run Plex stack indefinitely

### 🏋️‍♂️ New Hypervisor: Dell R730xd
- 2× Intel Xeon E5-2690 v4 (28 cores total)
- 128GB DDR4 RAM
- 4× 1.2TB SAS drives (to be configured with ZFS)
- 2TB Samsung 870 EVO SSD (Proxmox boot drive)
- 2× 10Gb SFP+ and 2× 1Gb NICs
- Will replace Pi4 for all service hosting via Proxmox VMs and containers
- Will replace Sonarr, Radarr, and Unpackarr from Windows Plex server

---

## 🌐 Network Architecture

Managed via **Ubiquiti Dream Machine Pro** + **USW 16 POE** with VLANs:

| VLAN        | Subnet         | Purpose                        |
|-------------|----------------|--------------------------------|
| 10.11.1.0   | Ubiquiti       | Network devices                |
| 10.11.10.0  | Main (Admin)   | Primary access                 |
| 10.11.20.0  | Kids Internet  | Restricted VLAN                |
| 10.11.30.0  | Servers        | R730xd, Plex PC, Pi4           |
| 10.11.40.0  | IoT            | Smart home devices/ Cameras    |
| 10.11.90.0  | Guest          | Guest WiFi                     |

---

## 🛠️ Planned Stack

| Layer         | Tool              | Purpose                               |
|---------------|-------------------|---------------------------------------|
| Hypervisor    | Proxmox VE        | Host VMs and LXCs                     |
| Provisioning  | Terraform         | Define VM/LXC specs and network setup |
| Configuration | Ansible           | Install Docker, configure services    |
| Containers    | Docker Compose    | Run self-hosted apps in containers    |
| Backup        | TBD               | Backup services, configs, and data    |

---

## 🧩 Migration Plan

I’m migrating all services off the Pi4 and onto the R730xd **one service at a time**. Each service will be assigned to a dedicated VM or LXC, depending on isolation and resource needs.

### Goals:
- Full reproducibility via Infrastructure-as-Code (IaC)
- Clean separation between compute, config, and storage
- Use Docker Compose to deploy apps inside VMs or LXCs
- Automate as much as possible from the Pi4

---

## 🗂️ Repo Structure (WIP)
```bash
homelabracadabra/
    ├── terraform/ # Define VMs, networking, storage
    │ └── README.md
    ├── ansible/ # Provision and configure systems
    │ └── README.md
    ├── docker/ # Compose files for services
    │ └── wikijs/
    │ └── paperless/
    │ └── ...
    ├── templates/ # Shared Terraform or Ansible roles
    ├── inventory/ # Static or dynamic Ansible inventory
    ├── docs/ # Diagrams, architecture notes, etc.
    └── README.md # This file
```


---

## ✅ Phase 1: Project Setup

- [x] Create `homelabracadabra` Git repository
- [x] Write root `README.md` (this file)

---

## 🛠 Phase 2: Infrastructure Setup

### R730xd Server
- [ ] Physically install and cable R730xd server
- [ ] Install **Proxmox VE** on 2TB SSD
- [ ] Configure ZFS storage on 4x 1.2TB SAS drives
- [ ] Join server to `10.11.30.0/24` (Servers VLAN)
- [ ] Set up SSH keys / admin access
- [ ] Configure DNS and hostname

### Pi 4 (Automation Controller)
- [ ] Fresh Pi OS install
- [ ] Install required tools: `git`, `ansible`, `terraform`, `docker`, etc.
- [ ] Clone this repo
- [ ] Create dedicated `README` for Pi setup
- [ ] Set up secure SSH access to all nodes

### Windows Plex Server
- [ ] Document and configure SMB shares for media storage
- [ ] Create `README` for Windows drive share setup
- [ ] Ensure network shares are mountable by containers/VMs (credentials, paths, etc.)
- [ ] Backup configuration planning

---

## ⚙️ Phase 3: Automation Stack

### Terraform
- [ ] Create `terraform/` folder
- [ ] Define VM/LXC provisioning plans for services
- [ ] Create module templates (memory, CPU, VLAN, disk)
- [ ] Include metadata to map services to VMs/LXCs
- [ ] Add README for provisioning system

### Ansible
- [ ] Create `ansible/` folder
- [ ] Playbooks for base VM setup (users, updates, mounts)
- [ ] Role-based structure for reusable service setup
- [ ] Secrets & vault setup
- [ ] Add README for structure and usage

### Docker
- [ ] Create `docker/` folder
- [ ] Modular `docker-compose.yml` templates per service
- [ ] Network configuration between services across containers/VMs
- [ ] Sample `.env` and `config.yml` files for customization
- [ ] Add README explaining service composition model

---

## 📦 Phase 4: Service Migration Plan

Each service will be migrated from the Pi to the Proxmox server, one at a time. Some VMs may host multiple containers.

| Service         | Status | Target VM/LXC        | Notes                                      |
|------------------|--------|----------------------|--------------------------------------------|
| PostgreSQL       | [ ]    | `db-core`            | Needed for multiple services               |
| Wiki.js          | [ ]    | `wiki-app`           | DB hosted on `db-core`                     |
| Paperless-ngx    | [ ]    | `paperless`          | Connect to shared media volume             |
| SWAG             | [ ]    | `reverse-proxy`      | Public reverse proxy, DNS handling         |
| Home Assistant   | [ ]    | `iot-core`           | VLAN 40, requires device passthrough       |
| Prometheus       | [ ]    | `metrics`            | Monitors all VMs and services              |
| Grafana          | [ ]    | `metrics`            | Dashboards and alerting                    |
| FlareSolverr     | [ ]    | `search-utils`       | Used by Jackett, Radarr, Sonarr            |
| Jackett          | [ ]    | `search-utils`       | Indexers                                   |
| OpenWebUI        | [ ]    | `llm-ui`             | Connects to Ollama on Windows Plex server  |

---

## 🧪 Bonus Plans

- [ ] Use Ansible to configure Windows shares via Samba mounts in containers
- [ ] Configure templated VM assignments via `terraform.tfvars`
- [ ] Add backup and restore scripts using restic or rsync
- [ ] Enable Proxmox API access for automated provisioning
- [ ] Optional: Monitor and update DNS records via Cloudflare API

---

## 📜 License

This project is licensed under the [MIT License](./LICENSE).

---

## 🙌 Inspiration

Inspired by the chaos and joy of self-hosting, and the satisfaction of typing `ansible-playbook deploy.yml` and watching services spin into life.

---