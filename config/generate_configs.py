import yaml
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_PATH = BASE_DIR / "config" / "homelab.yml"
TERRAFORM_OUTPUT = BASE_DIR / "terraform" / "auto_config.tfvars.json"
ANSIBLE_OUTPUT = BASE_DIR / "ansible" / "inventories" / "generated_inventory.yml"
DOCKER_ENV_OUTPUT = BASE_DIR / "docker" / ".env"
GROUP_VARS_DIR = BASE_DIR / "ansible" / "group_vars"


def load_config(path):
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    print("Loaded config keys:", config.keys())
    print("VMs found:", list(config.get("vms", {}).keys()))
    print("Docker containers found:", list(config.get("docker", {}).keys()))
    return config


def generate_terraform_vars(config):
    terraform_vars = {
        "vms": config.get("vms", {}),
        "network": config.get("network", {})
    }
    TERRAFORM_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(TERRAFORM_OUTPUT, "w") as f:
        json.dump(terraform_vars, f, indent=2)
    print(f"Terraform vars written to {TERRAFORM_OUTPUT}")

def generate_ansible_inventory(config):
    vms = config.get("vms", {})
    docker = config.get("docker", {})

    # Map VM names to host vars
    vm_hosts = {
        vm_data["name"]: {
            "ansible_host": vm_data["ip"],
            "ansible_user": vm_data["ssh_user"]
        }
        for vm_data in vms.values()
    }

    # Group containers by VM name (not config key)
    containers_by_vm = {}
    for container_name, container_conf in docker.items():
        vm_name = container_conf.get("vm")
        # Find VM data by matching "name" field
        vm_data = next((v for v in vms.values() if v.get("name") == vm_name), None)
        if not vm_data:
            print(f"Warning: container '{container_name}' references unknown VM '{vm_name}'. Skipping.")
            continue

        base_path = vm_data["base_data_dir"].rstrip('/')
        container_entry = {}

        if "data_dir" in container_conf:
            container_entry["data_dir"] = f"{base_path}/{container_conf['data_dir'].lstrip('/')}"
        if "media_dir" in container_conf:
            container_entry["media_dir"] = f"{base_path}/{container_conf['media_dir'].lstrip('/')}"
        if "port" in container_conf:
            container_entry["port"] = container_conf["port"]

        containers_by_vm.setdefault(vm_name, {})[container_name] = container_entry

    # Build inventory
    inventory = {"all": {"children": {}}}
    for vm_data in vms.values():
        vm_name = vm_data["name"]
        host_vars = vm_hosts[vm_name]

        inventory["all"]["children"][vm_name] = {
            "hosts": {vm_name: host_vars},
            "children": {}
        }

        for container_name, container_vars in containers_by_vm.get(vm_name, {}).items():
            inventory["all"]["children"][vm_name]["children"][container_name] = {
                "hosts": {
                    container_name: container_vars or {}
                }
            }

    ANSIBLE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(ANSIBLE_OUTPUT, "w") as f:
        yaml.dump(inventory, f, sort_keys=False)
    print(f"Ansible inventory written to {ANSIBLE_OUTPUT}")


def generate_group_vars_vms(config):
    import yaml

    vms = config.get("vms", {})
    print(f"Generating group_vars for VMs: {list(vms.keys())}")
    GROUP_VARS_DIR.mkdir(parents=True, exist_ok=True)

    for vm_key, vm_data in vms.items():
        print(f"Processing VM: {vm_key} with data: {vm_data}")
        vm_vars = {k: v for k, v in vm_data.items() if k != "name"}
        
        # Use the vm_key (e.g., 'postgres') as the group name
        vars_file = GROUP_VARS_DIR / f"{vm_key}.yml"
        
        with open(vars_file, "w") as f:
            yaml.dump(vm_vars, f, sort_keys=False)

        print(f"Group vars for VM '{vm_key}' written to {vars_file}")


def generate_docker_env(config):
    docker = config.get("docker", {})
    vms = config.get("vms", {})

    # Map VM name to VM key (e.g. 'postgres_vm' -> 'postgres')
    vm_name_to_key = {vm_data["name"]: vm_key for vm_key, vm_data in vms.items()}

    print(f"Generating docker env for containers: {list(docker.keys())}")
    env_lines = []
    for container_name, container_conf in docker.items():
        print(f"Container: {container_name}, config: {container_conf}")
        vm_name = container_conf.get("vm")
        vm_key = vm_name_to_key.get(vm_name)
        if not vm_key or vm_key not in vms:
            print(f"Warning: container '{container_name}' has invalid or missing VM '{vm_name}'. Skipping.")
            continue

        base_data_dir = vms[vm_key].get("base_data_dir", "/opt/data")
        data_dir = f"{base_data_dir}/{container_conf.get('data_dir', '')}".rstrip("/")
        media_dir = f"{base_data_dir}/{container_conf.get('media_dir', '')}".rstrip("/")

        env_lines.append(f"{container_name.upper()}_DATA_DIR={data_dir}")
        env_lines.append(f"{container_name.upper()}_MEDIA_DIR={media_dir}")

        for key, value in container_conf.items():
            if key in ["vm", "data_dir", "media_dir"]:
                continue
            env_lines.append(f"{container_name.upper()}_{key.upper()}={value}")

    DOCKER_ENV_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(DOCKER_ENV_OUTPUT, "w") as f:
        f.write("\n".join(env_lines))
    print(f"Docker .env written to {DOCKER_ENV_OUTPUT}")

def main():
    config = load_config(CONFIG_PATH)
    generate_terraform_vars(config)
    generate_ansible_inventory(config)
    generate_group_vars_vms(config)
    generate_docker_env(config)


if __name__ == "__main__":
    main()
