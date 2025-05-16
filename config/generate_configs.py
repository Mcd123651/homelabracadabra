import yaml
import json
from pathlib import Path

# Base path is the parent directory of this script
BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_PATH = BASE_DIR / "config" / "homelab.yaml"
TERRAFORM_OUTPUT = BASE_DIR / "terraform" / "auto_config.tfvars.json"
ANSIBLE_OUTPUT = BASE_DIR / "ansible" / "inventories" / "generated_inventory.yaml"
DOCKER_ENV_OUTPUT = BASE_DIR / "docker" / ".env"

# Load YAML config
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Write Terraform vars
terraform_vars = {
    k: v for section in config.values() if isinstance(section, dict)
    for k, v in section.items() if isinstance(v, (str, int, float, bool))
}
TERRAFORM_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with open(TERRAFORM_OUTPUT, "w") as f:
    json.dump(terraform_vars, f, indent=2)

# Write Ansible inventory
inventory = {
    "all": {
        "hosts": {
            vm["name"]: {
                "ansible_host": vm["ip"],
                "ansible_user": vm["ssh_user"]
            }
            for vm in config.get("vms", {}).values()
        }
    }
}
ANSIBLE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with open(ANSIBLE_OUTPUT, "w") as f:
    yaml.dump(inventory, f)

# Write Docker .env
env_lines = []
for section_name, section in config.get("docker", {}).items():
    for key, value in section.items():
        env_lines.append(f"{section_name.upper()}_{key.upper()}={value}")
DOCKER_ENV_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with open(DOCKER_ENV_OUTPUT, "w") as f:
    f.write("\n".join(env_lines))
