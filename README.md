# 🧙‍♂️ homelabracadabra

> *Because it's magic when it works.*

**homelabracadabra** is a magical collection of Infrastructure as Code (IaC) for conjuring up self-hosted services, virtual machines, containers, and automations.

Built with **Proxmox**, **Ansible**, **Terraform**, and **Docker**, this repo powers my homelab—but it’s designed to be **adaptable for others** too. Hardware-agnostic configurations, templated provisioning, and modular service definitions mean *you* can fork this project and shape it to your own wizardry.

Whether you’re running on a Raspberry Pi, a rackmount server, or just dreaming of your future setup, these scripts can be customized to suit your network, VM layout, and service stack.

Let’s automate some magic.


## Quick Links
- [🏠Homelab Overview](docs/HOMELAB_OVERVIEW.md)
- [🍓Pi4 Setup Guide](docs/PI4-README.md)


## Prerequisites

1. Have [proxmox](https://www.proxmox.com/en/) installed and your storage drives set up
2. Set up an orchestration node (In this guide I am using a PI4) 
3. Using the Pi4 guide make sure ansible and terraform are installed.

## Step 1. Building Infrastructure (VMs)

First you will need to clone this repo into your control node (Pi4 etc..)
```bash
git clone https://github.com/Mcd123651/homelabracadabra.git

cd homelabracadabra
```

Navigate to ```config/``` and rename ```homelab.yml.example``` to ```homelab.yml```

This file will serve as the master config for the enture homelab. For Phase 1 we are only going to manage the Global and VM sections:

Create a new SSH key to be used to ssh into the new vms:
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_lab -C "lab_ssh"
```

Edit the variables

```yml
# ======================
# Global Configuration
# ======================
proxmox:
  host: "192.168.100.10"               # Replace with your Proxmox host IP
  target_node: "lab-node"              # Replace with your actual node name ex. PVE

template:                              # Create Proxmox Templates to clone into VMs
  ubuntu:
    name: "ubuntu-cloudinit-template"  # Name of Template 
    image: "ubuntu-cloudimg-amd64.img" # Image of ubuntu template 
    vmid: 9000                         # Image of ubuntu template 
    datasource_id: "default-datastore" # Disc where you want the template to be saved 
    disk: 20                           # Template size 
    memory: 1024                       # Template memory 
    user: "labadmin"                   # SSH Username 
    ssh_key: "/home/user/.ssh/id_rsa_lab.pub"  # Control node public key
    tags: ["template", "ubuntu"]       # Proxmox tags

# ======================
# VM Configuration
# ======================
hosts:
  - name: vm-router           # Name of VM
    cores: 2                  # Number of cores
    memory: 4096              # RAM
    disk: 32                  # Storage size
    ip: 192.168.100.101/24    # Set ip address
    gateway: 192.168.100.1    # Set gateway
    template: 9000            # Template ID to clone

  - name: vm-database
    cores: 4
    memory: 8192
    disk: 64
    ip: 192.168.100.102/24
    gateway: 192.168.100.1
    template: 9000
```
TODO: Add implementation for dhcp
```bash
  initialization {
    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
```

### Next we will generate our terraform directory by executing an ansible script.

First create and activate a .venv enviornment at the root of the repository
```python
# Create
python3 -m venv .venv
# Activate
source .venv/bin/activate
```
Install Ansible
```python
sudo apt install -y software-properties-common
sudo apt-add-repository --yes --update ppa:ansible/ansible
sudo apt install -y ansible
```

Now execute:
```bash
ansible-playbook ansible/run_config_generator.yml
```