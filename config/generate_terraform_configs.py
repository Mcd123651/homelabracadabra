import os
import yaml
from pathlib import Path

# Updated template for bpg/proxmox provider
TEMPLATE = """
resource "proxmox_virtual_environment_vm" "{name}" {{
  # Configuration using the current bpg/proxmox provider syntax
  node_name = "{node_name}"
  vm_id     = {vmid}
  name      = "{name}"
  
  started   = true
  on_boot   = true
  
  clone {{
    vm_id = "{template}"
    full  = true
  }}
  
  cpu {{
    cores = {cores}
    sockets = 1
  }}
  
  memory {{
    dedicated = {memory}
  }}
  
  agent {{
    enabled = true
  }}
  
  disk {{
    interface = "scsi0"
    datastore_id = "local-zfs"
    size = "{disk}"
  }}
  
  network_device {{
    bridge = "vmbr0"
    model  = "virtio"
  }}
  
  initialization {{
    ip_config {{
      ipv4 {{
        address = "{ip}/"
        gateway = "{gateway}"
      }}
    }}
    
    user_account {{
      username = "{ssh_user}"
      password = var.default_password
      keys     = [file("{ssh_pub_key_path}")]
    }}
  }}
  
  tags = ["managed-by-terraform"]
}}
"""

VARIABLES_TF = """
variable "pm_api_url" {{
  description = "Proxmox API URL"
  type        = string
  default     = "https://{proxmox_host}:8006/api2/json"
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
"""

TFVARS_TEMPLATE = """# Fill in your Proxmox credentials
pm_api_url = "https://{proxmox_host}:8006/api2/json"
pm_user = "root@pam"
pm_password = "YOUR_PROXMOX_ROOT_PASSWORD"
pm_tls_insecure = true
default_password = "YOUR_VM_PASSWORD"
"""

def resolve_ssh_key_path(path):
    return str(Path(path).expanduser())

def load_config(yml_path):
    with open(yml_path, "r") as f:
        return yaml.safe_load(f)

def build_provider_tf(proxmox_host):
    return f"""
terraform {{
  required_providers {{
    proxmox = {{
      source  = "bpg/proxmox"
      version = ">= 0.50.0"
    }}
  }}
}}

provider "proxmox" {{
  endpoint      = var.pm_api_url
  username      = var.pm_user
  password      = var.pm_password
  insecure      = var.pm_tls_insecure
  ssh {{
    agent = true
  }}
}}
"""

def generate_main_tf(vms, provider_tf, output_dir, target_node):
    vm_blocks = []
    for vm in vms:
        # Ensure the disk size has the right format
        disk_size = f"{vm['disk']}"
        
        vm_block = TEMPLATE.format(
            name=vm["name"],
            node_name=target_node,
            template=vm["template"],
            vmid=vm["vmid"],
            cores=vm["cores"],
            memory=vm["memory"],
            disk=disk_size,
            ip=vm["ip"],
            gateway=vm["gateway"],
            ssh_user=vm["ssh_user"],
            ssh_pub_key_path=resolve_ssh_key_path(vm["ssh_pub_key_path"])
        )
        vm_blocks.append(vm_block)

    with open(os.path.join(output_dir, "main.tf"), "w") as f:
        f.write(provider_tf)
        f.write("\n\n")
        f.write("\n".join(vm_blocks))

def write_variables_tf(output_dir, proxmox_host):
    vars_content = VARIABLES_TF.format(proxmox_host=proxmox_host)
    with open(os.path.join(output_dir, "variables.tf"), "w") as f:
        f.write(vars_content)

def write_tfvars_if_missing(output_dir, proxmox_host):
    tfvars_path = os.path.join(output_dir, "terraform.tfvars")
    if not os.path.exists(tfvars_path):
        tfvars_content = TFVARS_TEMPLATE.format(proxmox_host=proxmox_host)
        with open(tfvars_path, "w") as f:
            f.write(tfvars_content)
        print(f"⚠️  'terraform.tfvars' created at {tfvars_path}. Please edit it with your actual secrets.")

def main():
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / "config" / "homelab.yml"
    terraform_dir = base_dir / "terraform"

    terraform_dir.mkdir(parents=True, exist_ok=True)

    config = load_config(config_path)
    proxmox_host = config.get("proxmox", {}).get("host", "proxmox.local")
    target_node = config.get("proxmox", {}).get("target_node", "homelab")
    vms = config.get("vms", [])

    provider_tf = build_provider_tf(proxmox_host)

    generate_main_tf(vms, provider_tf, terraform_dir, target_node)
    write_variables_tf(terraform_dir, proxmox_host)
    write_tfvars_if_missing(terraform_dir, proxmox_host)

    print(f"✅ Terraform files generated in: {terraform_dir}")
    print(f"🌐 Proxmox host set to: {proxmox_host}")

if __name__ == "__main__":
    main()