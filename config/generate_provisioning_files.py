import yaml
from pathlib import Path


def load_config(filename="homelab.yml"):
    script_dir = Path(__file__).resolve().parent
    config_path = script_dir / filename
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def ensure_terraform_dir(relative_path="../terraform_output"):
    script_dir = Path(__file__).resolve().parent
    output_path = (script_dir / relative_path).resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path

def ensure_ansible_dir(relative_path="../ansible"):
    script_dir = Path(__file__).resolve().parent
    output_path = (script_dir / relative_path).resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def generate_template_tf(config):
    template = config["template"]["ubuntu"]
    node = config["proxmox"]["target_node"]
    
    return f"""
resource "proxmox_virtual_environment_vm" "ubuntu_template" {{
  name      = "{template['name']}"
  node_name = "{node}"
  vm_id     = "{template['vmid']}"

  template = true
  started  = false

  machine     = "q35"
  description = "Managed by Terraform"

  agent {{
    enabled = false
  }}

  cpu {{
    cores = 2
  }}

  memory {{
    dedicated = {template.get('memory', 1024)}
  }}

  disk {{
    datastore_id = "{template['datasource_id']}"
    file_id      = proxmox_virtual_environment_download_file.ubuntu_cloud_image.id
    interface    = "virtio0"
    iothread     = true
    discard      = "on"
    size         = {template.get('disk', 2)}
  }}

  initialization {{
    datastore_id = "{template['datasource_id']}"
    user_account {{
      username = "{template['user']}"
      keys     = [file("{template['ssh_key']}")]
    }}
    ip_config {{
      ipv4 {{
        address = "dhcp"
      }}
    }}
  }}

  network_device {{
    bridge = "vmbr0"
  }}
}}

resource "proxmox_virtual_environment_download_file" "ubuntu_cloud_image" {{
  content_type = "iso"
  datastore_id = "local"
  node_name    = "{node}"

  url = "https://cloud-images.ubuntu.com/noble/current/{template['image']}"
}}
""".strip()


def generate_main_tf(config):
    template = config["template"]["ubuntu"]
    node = config["proxmox"]["target_node"]
    blocks = []

    # Track how many VMs we've created for each template ID
    template_usage_counts = {}

    for host in config["hosts"]:
        template_id = host["template"]
        current_count = template_usage_counts.get(template_id, 0)
        vm_id = template_id + 1 + current_count
        template_usage_counts[template_id] = current_count + 1

        blocks.append(f"""
resource "proxmox_virtual_environment_vm" "{host['name']}" {{
  name      = "{host['name']}"
  node_name = "{node}"
  vm_id     = {vm_id}

  depends_on = [proxmox_virtual_environment_vm.ubuntu_template]

  clone {{
    vm_id = {template_id}
    datastore_id = "{template['datasource_id']}"
  }}

  agent {{
    enabled = false
  }}

  cpu {{
    cores = {host['cores']}
  }}

  memory {{
    dedicated = {host['memory']}
  }}

  disk {{
    datastore_id = "{template['datasource_id']}"
    interface = "virtio0"
    size = {host['disk']}
  }}

  initialization {{
    datastore_id = "{template['datasource_id']}"
    ip_config {{
      ipv4 {{
        address = "{host['ip']}"
        gateway = "{host['gateway']}"
      }}
    }}
    user_account {{
      username = "{template['user']}"
      keys     = [file("{template['ssh_key']}")]
    }}
  }}

  network_device {{
    bridge = "vmbr0"
  }}
}}
""".strip())

    return "\n\n".join(blocks)


def generate_provider_tf():
    return """
terraform {
  required_providers {
    proxmox = {
      source  = "bpg/proxmox"
      version = ">= 0.50.0"
    }
  }
}

provider "proxmox" {
  endpoint      = var.pm_api_url
  username      = var.pm_user
  password      = var.pm_password
  insecure      = var.pm_tls_insecure
  ssh {
    agent = true
  }
}
""".strip()


def generate_variables_tf(config):
    host = config["proxmox"]["host"]
    return f"""
variable "pm_api_url" {{
  description = "Proxmox API URL"
  type        = string
  default     = "https://{host}:8006/api2/json"
}}

variable "pm_user" {{
  description = "Proxmox username"
  type        = string
  default     = "root@pam"
}}

variable "pm_password" {{
  description = "Proxmox password"
  type        = string
  sensitive   = true
}}

variable "pm_tls_insecure" {{
  description = "Allow insecure TLS connections"
  type        = bool
  default     = true
}}

variable "default_password" {{
  description = "Default password for VM users"
  type        = string
  sensitive   = true
}}

variable "virtual_environment_token" {{
  type        = string
  description = "The token for the Proxmox Virtual Environment API"
  sensitive   = true
}}
""".strip()

def generate_tfvars():
    return f"""
# Proxmox Vars
pm_password = "CHANGEME"

# User SSH PW
default_password = "CHANGEME"
""".strip()

def generate_ansible_inventory(config):
    hosts = config["hosts"]
    inventory_lines = ["[homelab]"]
    for host in hosts:
        ip = host["ip"].split("/")[0]
        inventory_lines.append(f"{host['name']} ansible_host={ip}")

    inventory_lines += [
        "\n[homelab:vars]",
        f"ansible_user={config['template']['ubuntu']['user']}",
        f"ansible_ssh_private_key_file={config['template']['ubuntu']['ssh_key'].replace('.pub', '')}",
        f"ansible_port={config['global']['vm_ssh_port']}",
        f"ansible_ssh_common_args='-o StrictHostKeyChecking=accept-new'"
    ]
    inventory_lines.append(f"subnets={' '.join(config['global']['subnets'])}")
    
    return "\n".join(inventory_lines)


def write_file(path, content):
    path.write_text(content)
    print(f"Written: {path}")

def main():
    config = load_config()
    output_dir = ensure_terraform_dir()
    ansible_dir = ensure_ansible_dir()

    write_file(output_dir / "template.tf", generate_template_tf(config))
    write_file(output_dir / "main.tf", generate_main_tf(config))
    write_file(output_dir / "provider.tf", generate_provider_tf())
    write_file(output_dir / "variables.tf", generate_variables_tf(config))
    write_file(output_dir / "terraform.tfvars.example", generate_tfvars())

    # New: Write Ansible inventory
    write_file(ansible_dir / "inventory.ini", generate_ansible_inventory(config))

    print(f"\nAll Terraform files written to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
