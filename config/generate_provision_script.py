import os
import stat
from pathlib import Path
import yaml

PROVISION_SCRIPT = """#!/bin/bash

set -e

echo "🔐 Exporting secrets from terraform.tfvars..."
export TF_VAR_pm_password=$(jq -r '.pm_password' terraform/terraform.tfvars)
export TF_VAR_default_password=$(jq -r '.default_password' terraform/terraform.tfvars)

echo "🚀 Running Terraform to provision VMs..."
cd terraform
terraform init
terraform apply -auto-approve
cd ..

{ssh_setup}

{ansible_block}

{docker_block}

echo "✅ Homelab provisioning complete."
"""

SSH_SETUP = """# SSH setup (optional Pi4 SSH into VMs)
# ssh-copy-id -i ~/.ssh/id_rsa.pub homelab@VM_IP
# Example:
# ssh homelab@192.168.1.101
"""

ANSIBLE_BLOCK = """echo "📦 Running Ansible playbook..."
cd ansible
ansible-playbook -i inventory.ini playbook.yml
cd ..
"""

DOCKER_BLOCK = """# Optional: Docker setup on VMs
# ssh homelab@VM_IP 'bash -s' < setup-docker.sh
"""

def load_config():
    config_path = Path("config/homelab.yml")
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return yaml.safe_load(f)

def generate_script(config, output_path="scripts/provision.sh"):
    include_ansible = config.get("ansible", True)
    include_docker = config.get("docker", False)

    script = PROVISION_SCRIPT.format(
        ssh_setup=SSH_SETUP,
        ansible_block=ANSIBLE_BLOCK if include_ansible else "# (Ansible step skipped)",
        docker_block=DOCKER_BLOCK if include_docker else "# (Docker setup skipped)"
    )

    with open(output_path, "w") as f:
        f.write(script)

    # Make executable
    st = os.stat(output_path)
    os.chmod(output_path, st.st_mode | stat.S_IEXEC)

    print(f"📝 Generated {output_path}")

if __name__ == "__main__":
    cfg = load_config()
    generate_script(cfg)
