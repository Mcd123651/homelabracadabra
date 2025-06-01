# 🧙‍♂️ homelabracadabra

> *Because it's magic when it works.*

**homelabracadabra** is a magical collection of Infrastructure as Code (IaC) for conjuring up self-hosted services, virtual machines, containers, and automations.

Built with **Proxmox**, **Ansible**, **Terraform**, and **Docker**, this repo powers my homelab—but it's designed to be **adaptable for others** too. Hardware-agnostic configurations, templated provisioning, and modular service definitions mean *you* can fork this project and shape it to your own wizardry.

Whether you're running on a Raspberry Pi, a rackmount server, or just dreaming of your future setup, these scripts can be customized to suit your network, VM layout, and service stack.

Let's automate some magic.

## 🏗️ Architecture Overview

This homelab automation follows a **staged deployment approach** using a central `homelab.yml` configuration file that drives multiple Ansible playbooks. Each stage builds upon the previous one, creating a fully automated infrastructure from bare VMs to production-ready services.

```
homelab.yml → Generate → Generate → Bootstrap → Provision → Deploy → Mount SMB
   Config      Configs     VMs        VMs        VMs        Services   Shares
```

## 🎯 How It Works

Using a master `homelab.yml` config file and a suite of ansible playbooks, this repository enables fully automated deployment through six distinct stages:

## 🔗 Quick Links

- [🍓 Pi 4 Homelab Controller Setup Guide](docs/PI4-README.md)
- [☁️ Cloudflare Tunnel Setup Guide](docs/CF_TUNNEL_README.md)
- [🔧 Configuration Examples](config/homelab.yml.example)
- [🛠️ Adding Custom Services](#-adding-custom-services)
- [🐛 Troubleshooting Guide](#-troubleshooting)

### Stage 1: Generate Configurations
**Playbook:** `01-generate_configs.yml`

Generates Terraform and Ansible scripts dynamically based on your `config/homelab.yml` configuration using Python helper scripts.

**What it does:**
- Executes `generate_provisioning_files.py` to create Terraform configurations
- Runs `generate_service_roles.py` to create service-specific Ansible roles
- Generates `inventory.ini` for Ansible host management
- Creates `05-deploy_services.yml` playbook based on service definitions
- Outputs all generated files to `terraform_output/` directory

**Key Config Sections:**
- `global` - Global settings like SSH ports and subnets
- `proxmox` - Proxmox host configuration
- `template` - VM template specifications
- `hosts` - Target VM definitions
- `services` - Service deployment configurations

### Stage 2: Generate VMs
**Playbook:** `02-generate_vms.yml`

Executes Terraform to initialize and apply infrastructure, launching VM templates and host instances.

**What it does:**
- Runs `terraform init` to initialize the Terraform workspace
- Executes `terraform apply` to create VM templates and clone host VMs
- Provisions VMs based on the `hosts` configuration
- Sets up networking and storage according to specifications

**Key Config Sections:**
- `template.ubuntu` - Ubuntu template configuration and cloud-init settings
- `hosts` - VM specifications including cores, memory, disk, and networking
- `proxmox.target_node` - Target Proxmox node for VM deployment

### Stage 3: Bootstrap VMs
**Playbook:** `03-bootstrap_vms.yml`

Bootstraps and secures the VMs by implementing security best practices and network configuration.

**What it does:**
- Changes SSH ports from default (22) to custom ports defined in global config
- Removes password authentication, enforcing SSH key-only access
- Configures firewall rules for the specified subnets
- Sets up basic system security and access controls

**Key Config Sections:**
- `global.vm_ssh_port` - Custom SSH port configuration
- `global.subnets` - Allowed network subnets
- `template.ubuntu.ssh_key` - SSH public key for authentication

### Stage 4: Provision VMs
**Playbook:** `04-provision_vms.yml`

Installs and configures Docker along with other essential software on all target VMs.

**What it does:**
- Installs Docker Engine and Docker Compose
- Configures Docker daemon with optimal settings
- Sets up necessary directories and permissions
- Prepares VMs for service deployment

**Key Config Sections:**
- `hosts` - Target VMs for Docker installation
- `services` - Services that will require Docker runtime

### Stage 5: Deploy Services
**Playbook:** `05-deploy_services.yml`

Deploys containerized services to VMs based on the generated configurations from Stage 1.

**What it does:**
- Deploys Cloudflared tunnels for secure external access
- Sets up Authelia authentication with PostgreSQL backend
- Configures SWAG reverse proxy with SSL/TLS
- Deploys PostgreSQL databases and other core services
- Orchestrates service deployment based on `deploy_order`

**Key Config Sections:**
- `services.cloudflared` - Cloudflare tunnel configuration
- `services.authelia` - Authentication server settings with database config
- `services.swag` - Reverse proxy and SSL configuration
- `services.postgres_db` - Database server and additional databases

### Stage 6 (Optional): Mount SMB Shares
**Playbook:** `99-mount_smb_shares.yml`

Configures SMB/CIFS mounting from Windows share servers for centralized storage access.

**What it does:**
- Installs CIFS utilities on target VMs
- Creates mount points for Windows shares
- Configures persistent mounting via fstab
- Sets up proper permissions and access controls

**Key Config Sections:**
- `smb_shares.server` - SMB server connection details
- `smb_shares.shares` - Individual share definitions and mount points
- `smb_shares.uid/gid` - User/group permissions for mounted shares

## 📋 Prerequisites

1. **Proxmox Environment**
   - [Proxmox VE](https://www.proxmox.com/en/) installed and configured
   - Storage drives and pools configured
   - Network bridges and VLANs set up

2. **Orchestration Node**
   - Dedicated node (Raspberry Pi 4 recommended) with:
     - Python 3.8+
     - Ansible 2.9+
     - Terraform 1.0+
   - Network access to Proxmox and target VMs

3. **SSH Key Authentication**
   - Generated SSH key pair for orchestration node
   - Public key ready for deployment to VMs

4. **External Services** 
   - Cloudflare account with API tokens
   - (Optional) Windows file server for SMB shares

## 🚀 Quick Start

1. **Clone and Configure**
   ```bash
   git clone https://github.com/Mcd123651/homelabracadabra.git
   cd homelabracadabra
   cp config/homelab.yml.example config/homelab.yml
   ```

2. **Edit Configuration**
   Customize `config/homelab.yml` with your environment details:
   - Proxmox connection settings
   - VM specifications and networking
   - Security policies and firewall rules
   - Service configurations

3. **Deploy Infrastructure**
   ```bash
   # deploy individual stages
   ansible-playbook -i inventory _01_generate_configs.yml
   ansible-playbook -i inventory _02_generate_vms.yml
   # ... continue with remaining stages
   ```

## 📁 Repository Structure

```
ansible/
  ├── site.yml                        # TODO: Main playbook that orchestrates all stages
  ├── inventory.ini                   # GENERATED: Ansible inventory files
  ├── 01-generate_configs.yml         
  ├── 02-generate_vms.yml             
  ├── 03-bootstrap_vms.yml            
  ├── 04-provision_vms.yml            
  ├── 05-deploy_services.yml          # GENERATED
  ├── 99-mount_smb_shares.yml         
  ├── roles/                          # Ansible roles for each component
  └── group_vars/                     # Group-specific variables

config/                                 
  ├── homelab.yml                     # Main configuration file
  ├── generate_provisioning_files.py  # Used by 01-generate_configs.yml
  └── generate_service_roles.py       # Used by 01-generate_configs.yml

docs/
  └── README_FILES

templates/
  ├── swag/
  ├── authelia/
  ├── cloudflared/
  ├── postgres_db/
  └── [your_custom_service]/          # Your custom service templates

terraform_output/                   # GENERATED: 01-generate_configs.yml
```

## 🔧 Configuration Deep Dive

The `config/homelab.yml` file is the heart of your infrastructure definition. Here's how it maps to each deployment stage:

### Sample Configuration Structure

```yaml
# ======================
# Global Configuration
# ======================
global:
  vm_ssh_port: 2222
  subnets: ["192.168.100.0/24", "192.168.110.0/24"] # Supports IPs

# Proxmox Configuration (Stage 2)
proxmox:
  host: "192.168.100.10"
  target_node: "lab-node"

# Template Configuration (Stage 2)
template:
  ubuntu:
    name: "ubuntu-2404-cloudinit-template"
    image: "custom-server-cloudimg-amd64.img"
    vmid: 9000
    datasource_id: "labvms"
    disk: 15
    memory: 1024
    user: "labuser"
    ssh_key: "/home/labuser/.ssh/id_rsa_lab.pub"
    tags: ["template", "ubuntu"]

# SMB Shares Configuration (Stage 6)
smb_shares:
  server: "192.168.100.20"
  user: "user@example.com"
  password: "ChangeMe123!"
  uid: 1000
  gid: 1000
  shares:
    - name: media
      share: MediaShare
      mount_point: /mnt/media
    - name: torrents
      share: TorrentsShare
      mount_point: /mnt/torrents

# ======================
# VM Configuration (Stage 2)
# ======================
hosts:
  - name: vm-database01
    cores: 4
    memory: 8192
    disk: 64
    ip: 192.168.100.101/24
    gateway: 192.168.100.1
    template: 9000
    deploy_order: 1

  - name: vm-networking01
    cores: 2
    memory: 8192
    disk: 32
    ip: 192.168.100.102/24
    gateway: 192.168.100.1
    template: 9000
    deploy_order: 2

# ======================
# Core Services Configuration (Stage 5)
# ======================
services:
  - name: cloudflared  
    vm: vm-networking01 # must be same as swag
    timezone: America/New_York
    cloudflared_tunnel_token: "example-tunnel-token-1234567890abcdef"
    
  - name: authelia  
    vm: vm-networking01 # must be same as swag
    timezone: America/New_York
    port: 9091
    url: example.com
    jwt_secret: "replace-with-jwt-secret"
    session_secret: "replace-with-session-secret"
    storage: postgres   # postgres or sqllite | deploy postgres first if selected
    storage_encryption_key: "replace-with-storage-encryption-key"
    postgres_host: 192.168.100.101   # postgres only
    postgres_port: 5432              # postgres only
    postgres_db: authelia            # postgres only
    postgres_user: authelia_user     # postgres only
    postgres_pw: authelia_password   # postgres only
    admin_user: adminuser
    admin_email: admin@example.com
    guest_user: guestuser
    notifier: smtp                          # smtp (gmail only) or file 
    smtp_username: "smtpuser@example.com"   # smtp only
    smtp_gmail_app_pw: "smtp-app-password"  # smtp only ... not gmail pw!
    
  - name: swag
    vm: vm-networking01
    timezone: America/New_York
    url: example.com
    dns_cloudflare_api_token: "replace-with-cloudflare-api-token"
    homepage_url: http://192.168.100.200:5055
    authelia: false                   # True includes authelia in SWAG proxy config files
    
  - name: postgres_db               
    vm: vm-database01 
    postgres_db: homelab
    port: 5432
    additional_dbs: ["authelia", "wikijs"]
```

## 🛠️ Adding Custom Services

One of the most powerful features of homelabracadabra is its extensibility. You can easily add your own services by following the established template pattern. Here's how to extend your homelab with custom services:

### Step 1: Add Service to Configuration

First, add your new service to the `services` section of your `config/homelab.yml`:

```yaml
services:
  # ... existing services ...
  
  - name: my_custom_service
    vm: vm-networking01
    timezone: America/New_York
    port: 8080
    custom_param1: "value1"
    custom_param2: "value2"
    environment_vars:
      - "VAR1=value1"
      - "VAR2=value2"
```

### Step 2: Create Service Template Directory

Create a new directory in `templates/` matching your service name:

```bash
templates/my_custom_service/
├── docker-compose.yml.j2
├── tasks_main.yml.j2
└── README.md.j2
```

### Step 3: Define Service Templates

#### **docker-compose.yml.j2**
This is your Docker Compose configuration with Jinja2 templating:

```yaml
version: '3.8'

services:
  {{ service.name }}:
    image: my-custom-app:latest
    container_name: {{ service.name }}
    restart: unless-stopped
    ports:
      - "{{ service.port }}:8080"
    environment:
      - TZ={{ service.timezone }}
{% if service.environment_vars is defined %}
{% for env_var in service.environment_vars %}
      - {{ env_var }}
{% endfor %}
{% endif %}
    volumes:
      - ./config:/app/config
      - ./data:/app/data
    networks:
      - homelab_network

networks:
  homelab_network:
    external: true
```

#### **tasks_main.yml.j2**
This defines the Ansible tasks for deploying your service:

```yaml
- name: Create {{ service.name }} config directory
  file:
    path: "{{ ansible_user_dir }}/{{ service.name }}"
    state: directory

- name: Create {{ service.name }} data directories
  file:
    path: "{{ ansible_user_dir }}/{{ service.name }}/{{ item }}"
    state: directory
  loop:
    - config
    - data

- name: Deploy docker-compose.yml
  template:
    src: docker-compose.yml.j2
    dest: "{{ ansible_user_dir }}/{{ service.name }}/docker-compose.yml"

- name: Deploy README.md
  template:
    src: README.md.j2
    dest: "{{ ansible_user_dir }}/{{ service.name }}/README.md"

- name: Start {{ service.name }} with docker compose
  shell: docker compose up -d
  args:
    chdir: "{{ ansible_user_dir }}/{{ service.name }}"

- name: Wait for {{ service.name }} to become available
  uri:
    url: "http://localhost:{{ service.port }}/health"
    method: GET
  register: service_health
  retries: 10
  delay: 5
  until: service_health.status == 200
  ignore_errors: yes

- name: Display service status
  debug:
    msg: "{{ service.name }} is running on port {{ service.port }}"
```

#### **README.md.j2**
Documentation for your deployed service:

```markdown
# {{ service.name | title }} Service

## Overview
This service is deployed on {{ service.vm }} and accessible on port {{ service.port }}.

## Configuration
- **Container Name**: {{ service.name }}
- **Port**: {{ service.port }}
- **Timezone**: {{ service.timezone }}

## Access
- **Local**: http://{{ service.vm }}:{{ service.port }}
- **External**: Available through SWAG reverse proxy if configured

## Management
```bash
# Navigate to service directory
cd ~/{{ service.name }}

# View logs
docker compose logs -f

# Restart service
docker compose restart

# Update service
docker compose pull && docker compose up -d
```

## File Locations
- **Config**: `~/{{ service.name }}/config/`
- **Data**: `~/{{ service.name }}/data/`
- **Compose File**: `~/{{ service.name }}/docker-compose.yml`
```

### Real-World Example: Adding Jellyfin Media Server

Here's a complete example of adding Jellyfin to your homelab:

#### **Configuration in homelab.yml:**
```yaml
services:
  - name: jellyfin
    vm: vm-media01
    timezone: America/New_York
    port: 8096
    media_path: /mnt/media
    config_path: /opt/jellyfin/config
    cache_path: /opt/jellyfin/cache
```

#### **templates/jellyfin/docker-compose.yml.j2:**
```yaml
version: '3.8'

services:
  jellyfin:
    image: jellyfin/jellyfin:latest
    container_name: {{ service.name }}
    restart: unless-stopped
    ports:
      - "{{ service.port }}:8096"
    environment:
      - TZ={{ service.timezone }}
      - JELLYFIN_PublishedServerUrl=http://{{ service.vm }}:{{ service.port }}
    volumes:
      - {{ service.config_path }}:/config
      - {{ service.cache_path }}:/cache
      - {{ service.media_path }}:/media:ro
    devices:
      - /dev/dri:/dev/dri  # For hardware acceleration
    networks:
      - homelab_network

networks:
  homelab_network:
    external: true
```

#### **templates/jellyfin/tasks_main.yml.j2:**
```yaml
- name: Create {{ service.name }} directories
  file:
    path: "{{ item }}"
    state: directory
    owner: "{{ ansible_user }}"
    group: "{{ ansible_user }}"
    mode: '0755'
  loop:
    - "{{ ansible_user_dir }}/{{ service.name }}"
    - "{{ service.config_path }}"
    - "{{ service.cache_path }}"

- name: Deploy docker-compose.yml
  template:
    src: docker-compose.yml.j2
    dest: "{{ ansible_user_dir }}/{{ service.name }}/docker-compose.yml"

- name: Deploy README.md
  template:
    src: README.md.j2
    dest: "{{ ansible_user_dir }}/{{ service.name }}/README.md"

- name: Start {{ service.name }} with docker compose
  shell: docker compose up -d
  args:
    chdir: "{{ ansible_user_dir }}/{{ service.name }}"

- name: Wait for {{ service.name }} to become available
  uri:
    url: "http://localhost:{{ service.port }}"
    method: GET
  register: jellyfin_health
  retries: 15
  delay: 10
  until: jellyfin_health.status == 200
  ignore_errors: yes

- name: Display {{ service.name }} access information
  debug:
    msg: |
      {{ service.name | title }} is now running!
      Access it at: http://{{ service.vm }}:{{ service.port }}
      Complete the setup wizard in your browser.
```

### Advanced Service Templates

For more complex services, you can include additional features:

#### **Database Dependencies:**
```yaml
- name: Wait for database to be ready
  shell: docker exec postgres_db pg_isready -U {{ service.db_user }} -d {{ service.db_name }}
  register: db_ready
  retries: 10
  delay: 3
  until: db_ready.rc == 0
```

#### **Configuration File Templates:**
```yaml
- name: Deploy service configuration
  template:
    src: app.conf.j2
    dest: "{{ ansible_user_dir }}/{{ service.name }}/config/app.conf"
  notify: restart service
```

#### **Conditional Tasks:**
```yaml
- name: Setup LDAP authentication
  template:
    src: ldap.conf.j2
    dest: "{{ ansible_user_dir }}/{{ service.name }}/config/ldap.conf"
  when: service.auth_method == "ldap"
```

### Best Practices for Custom Services

1. **Use Descriptive Variable Names**: Make your templates readable with clear variable names
2. **Include Health Checks**: Always verify your service starts correctly
3. **Document Everything**: Use comprehensive README templates
4. **Handle Dependencies**: Check for required services before deployment
5. **Use Proper File Permissions**: Ensure containers can access mounted volumes
6. **Test Thoroughly**: Validate your templates before committing

### Regenerating Service Roles

After adding new service templates, regenerate your deployment configuration:

```bash
ansible-playbook -i inventory 01-generate_configs.yml
```

This will automatically:
- Detect your new service templates
- Generate corresponding Ansible roles
- Update the deployment playbook
- Prepare everything for Stage 5 deployment

Your custom services will now be deployed alongside the core services during the standard deployment process!

## 🔐 Security Best Practices

This automation implements several security layers:

- **Network Isolation**: Each VM is firewalled by default with explicit allowlists
- **SSH Hardening**: Custom ports, key-only authentication, fail2ban protection
- **Zero Exposed Ports**: All external access through encrypted Cloudflare tunnels
- **Centralized Authentication**: Authelia provides SSO with MFA capabilities
- **Encrypted Storage**: All sensitive data encrypted at rest and in transit

## 🎭 Customization & Adaptation

The beauty of homelabracadabra lies in its adaptability. Fork this repository and customize it for your environment:

- **Hardware Agnostic**: Runs on anything from Raspberry Pi to enterprise servers
- **Modular Design**: Enable/disable stages based on your requirements
- **Templated Configs**: Easy to modify for different network layouts
- **Service Flexibility**: Add/remove services by updating the configuration

## 🐛 Troubleshooting

Common issues and solutions:

- **SSH Connection Failures**: Check firewall rules and SSH port configuration
- **Proxmox API Errors**: Verify API credentials and network connectivity
- **Docker Permission Issues**: Ensure proper user groups and volume permissions
- **Cloudflare Tunnel Issues**: Validate tunnel tokens and DNS configuration

## 🤝 Contributing

Contributions are welcome! Whether it's bug fixes, feature additions, or documentation improvements, feel free to submit pull requests.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*May your deployments be swift and your uptime eternal.* ✨