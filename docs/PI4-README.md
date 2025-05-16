🡐[🧙‍♂️ homelabracadabra](../README.md)

# 🍓 Pi 4 Homelab Controller Setup

This guide will walk you through setting up your Raspberry Pi 4 as the automation hub for `homelabracadabra`. It will act as the controller for deploying and managing VMs, containers, and services across your homelab using Terraform, Ansible, and Git.

---

## 🔧 Hardware Requirements

- Raspberry Pi 4 (2GB+ RAM recommended)
- 32GB+ microSD card (or external SSD for better performance)
- Reliable power supply
- Network connection (wired preferred)

---

## 🖥️ OS Installation

1. Download [Raspberry Pi OS Lite (64-bit)](https://www.raspberrypi.com/software/operating-systems/).
2. Flash to SD card using [Raspberry Pi Imager](https://www.raspberrypi.com/software/):
   - Enable SSH (under advanced settings)
   - Set hostname (e.g., `pi-controller`)
   - Configure Wi-Fi if needed (wired recommended)

3. Boot the Pi and SSH into it:

```bash
ssh pi@pi-controller.local
```

# 🧹 Initial Setup

```bash
sudo apt update && sudo apt upgrade -y
sudo raspi-config
```

In `raspi-config`, ensure:

- Set correct locale/timezone
- Enable SSH
- Set GPU memory to 16MB

# 🧰 Install Required Tools

Install Git and common utilities:
```bash
sudo apt install -y git curl unzip net-tools tmux
```

Install Docker:
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG 
```

Install Ansible:
```bash
sudo apt install -y software-properties-common
sudo apt-add-repository --yes --update ppa:ansible/ansible
sudo apt install -y ansible
```

Install Terraform:
```bash
sudo apt install -y gnupg software-properties-common
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

# 🛠️ Clone the Homelab Repo

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/homelabracadabra.git
cd homelabracadabra
```

# 🔐 SSH Access to Nodes

Set up SSH key (if not already):
```bash
ssh-keygen -t ed25519 -C "pi@homelab"
```
Copy the key to your nodes (e.g. Proxmox server, VMs, etc.):
```bash
ssh-copy-id user@hostname
```
Test that you can connect to all relevant machines without a password.

# 🧪 Test Automation Tool Versions

```bash
git --version
ansible --version
terraform -v
docker --version
```

# 🌐 Optional: Set a Static IP

I will be utilizing my DMP to set a static IP for the Pi4.

Edit `dhcpcd.conf`:
```bash
sudo nano /etc/dhcpcd.conf
```
Example for VLAN 30 (servers):
```bash
interface eth0
static ip_address=10.11.30.5/24
static routers=10.11.30.1
static domain_name_servers=10.11.30.1
```

# 🧙‍♂️ Tips

- Use `tmux` to keep scripts running even if your SSH session drops.
- Regularly backup the Pi SD card if you're not using an SSD.
- Use `.env` files and `vault.yml` for secrets handling.
```bash
Let me know if you'd like:

- A `setup.sh` script version of the manual steps
- A `systemd` service to auto-run updates/deploys
- A Pi monitoring dashboard via Prometheus/Grafana
- Instructions for attaching an SSD instead of SD card for boot
```