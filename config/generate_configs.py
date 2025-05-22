import os
import yaml
from pathlib import Path

# Template for a Proxmox VM resource
TEMPLATE = """
resource "proxmox_vm_qemu" "{name}" {{
  name        = "{name}"
  target_node = "proxmox"
  clone       = "{template}"
  vmid        = {vmid}
  cores       = {cores}
  memory      = {memory}
  agent       = 1
  os_type     = "cloud-init"
  ipconfig0   = "ip={ip},gw={gateway}"
  sshkeys     = file("{ssh_pub_key_path}")
  ciuser      = "{ssh_user}"
  cipassword  = var.default_password

  disk {{
    type    = "scsi"
    storage = "local-zfs"
    size    = "{disk}"
  }}

  network {{
    model  = "virtio"
    bridge = "vmbr0"
  }}

  tags = "managed-by-terraform"
}}
"""

# Variable definitions
VARIABLES_TF = """
variable "pm_password" {
  description = "Proxmox root password"
  type        = string
  sensitive   = true
}

variable "default_password" {
  description = "Default password for VM users"
  type        = string
  sensitive   = true
}
"""

# Provider block
PROVIDER_TF = """
provider "proxmox" {
  pm_api_url      = "https://proxmox.local:8006/api2/json"
  pm_user         = "root@pam"
  pm_password     = var.pm_password
  pm_tls_insecure = true
}
"""

TFVARS_TEMPLATE = """# Fill in your Proxmox credentials
pm_password = "YOUR_PROXMOX_ROOT_PASSWORD"
default_password = "YOUR_VM_PASSWORD"
"""

def resolve_ssh_key_path(path):
    return str(Path(path).expanduser())

def load_config(yml_path):
    with open(yml_path, "r") as f:
        return yaml.safe_load(f)

def generate_main_tf(vms, output_dir):
    vm_blocks = []
    for vm in vms:
        vm_block = TEMPLATE.format(
            name=vm["name"],
            template=vm["template"],
            vmid=vm["vmid"],
            cores=vm["cores"],
            memory=vm["memory"],
            disk=vm["disk"],
            ip=vm["ip"],
            gateway=vm["gateway"],
            ssh_user=vm["ssh_user"],
            ssh_pub_key_path=resolve_ssh_key_path(vm["ssh_pub_key_path"])
        )
        vm_blocks.append(vm_block)

    with open(os.path.join(output_dir, "main.tf"), "w") as f:
        f.write(PROVIDER_TF)
        f.write("\n")
        f.write("\n".join(vm_blocks))

def write_variables_tf(output_dir):
    with open(os.path.join(output_dir, "variables.tf"), "w") as f:
        f.write(VARIABLES_TF)

def write_tfvars_if_missing(output_dir):
    tfvars_path = os.path.join(output_dir, "terraform.tfvars")
    if not os.path.exists(tfvars_path):
        with open(tfvars_path, "w") as f:
            f.write(TFVARS_TEMPLATE)
        print(f"⚠️  'terraform.tfvars' created at {tfvars_path}. Please edit it with your actual secrets.")

def main():
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / "config" / "homelab.yml"
    terraform_dir = base_dir / "terraform"

    terraform_dir.mkdir(parents=True, exist_ok=True)

    config = load_config(config_path)
    vms = config.get("vms", [])

    generate_main_tf(vms, terraform_dir)
    write_variables_tf(terraform_dir)
    write_tfvars_if_missing(terraform_dir)

    print(f"✅ Terraform files generated in: {terraform_dir}")

if __name__ == "__main__":
    main()
