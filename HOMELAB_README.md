# Homelab Setup Documentation

## Project Overview
This homelab configuration includes:
- **Authelia**: Multi-factor authentication service with Docker compose and Jinja2 templates
- **Cloudflared**: Reverse proxy with TLS termination and Cloudflare API integration
- **SWAG**: Web application gateway with Let's Encrypt support
- **PostgreSQL**: Database service with Docker compose configuration
- **Ansible playbooks**: For configuration generation, VM provisioning, and system bootstrapping
- **Terraform**: Infrastructure-as-code configurations for cloud resources

## Stages of Homelab Setup
1. **Prerequisites** - Install required software (Ansible, Docker, Git)
2. **Repository Setup** - Clone repository and configure variables in `homelab.yml`
3. **Configuration Generation** - Run `_01_generate_configs.yml` to create service templates
4. **VM Provisioning** - Execute `_02_generate_vms.yml` to define virtual machines
5. **System Bootstrapping** - Apply `_03_bootstrap_vms.yml` for initial system setup
6. **Service Deployment** - Use `_04_provision_vms.yml` to deploy all services
7. **Post-Deployment** - Mount SMB shares and configure final settings

## Directory Structure
```
├── ansible/              # Ansible playbooks and roles
│   ├── _01_generate_configs.yml
│   ├── _02_generate_vms.yml
│   └── roles/            # Ansible roles for various services
├── config/               # Configuration files and scripts
│   ├── generate_provisioning_files.py
│   └── homelab.yml.example
├── templates/            # Jinja2 templates for service configurations
│   ├── authelia/
│   ├── cloudflared/
│   └── swag/
├── terraform_output/     # Infrastructure-as-code configurations
└── docs/                 # Documentation files
    ├── HOMELAB_OVERVIEW.md
    ├── PI4-README.md
    └── VM_CONFIG_README.md
```

## Key Components
### 1. Authelia
- Provides multi-factor authentication
- Uses `authelia.subdomain.conf.j2` template
- Docker compose configuration in `docker-compose.yml.j2`

### 2. Cloudflared
- Reverse proxy with TLS termination
- Configuration in `.env.j2` and `docker-compose.yml.j2`
- Cloudflare API integration

### 3. SWAG
- Web application gateway
- Uses `cloudflare.ini.j2` for configuration
- Docker compose template in `docker-compose.yml.j2`

## Setup Instructions
1. **Prerequisites**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install ansible docker.io git -y
   ```

2. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/homelab.git
   cd homelab
   ```

3. **Configure Variables**
   Edit `config/homelab.yml.example` and rename to `homelab.yml`

4. **Run Ansible Playbook**
   ```bash
   ansible-playbook -i inventory.ini _01_generate_configs.yml
   ```

5. **Provision VMs**
   ```bash
   ansible-playbook -i inventory.ini _02_generate_vms.yml
   ```

6. **Bootstrap VMs**
   ```bash
   ansible-playbook -i inventory.ini _03_bootstrap_vms.yml
   ```

7. **Provision Services**
   ```bash
   ansible-playbook -i inventory.ini _04_provision_vms.yml
   ```

## Service Management
- **Authelia**: `docker-compose -f templates/authelia/docker-compose.yml.j2 up -d`
- **Cloudflared**: `docker-compose -f templates/cloudflared/docker-compose.yml.j2 up -d`
- **SWAG**: `docker-compose -f templates/swag/docker-compose.yml.j2 up -d`

## Documentation
- Full overview: `docs/HOMELAB_OVERVIEW.md`
- Raspberry Pi 4 setup: `docs/PI4-README.md`
- VM configuration details: `docs/VM_CONFIG_README.md`

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a pull request
