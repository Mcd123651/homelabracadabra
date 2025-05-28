from pathlib import Path
import yaml
import shutil
import jinja2
from jinja2 import Environment, FileSystemLoader, meta
import textwrap

BASE_DIR = Path(__file__).parent.resolve()
CONFIG_PATH = BASE_DIR / "homelab.yml"
TEMPLATES_PATH = BASE_DIR.parent / "templates"
ANSIBLE_ROLES_PATH = BASE_DIR.parent / "ansible" / "roles"
PLAYBOOKS_DIR = BASE_DIR.parent / "ansible" / "playbooks"

KNOWN_ANSIBLE_VARS = {
    "ansible_user_dir",
    "inventory_hostname",
    "ansible_hostname",
    "ansible_os_family",
    "ansible_distribution",
    "ansible_architecture",
    "ansible_facts",
    "ansible_env",
    # add more as needed
}

def load_config():
    with CONFIG_PATH.open() as f:
        return yaml.safe_load(f)

def extract_jinja_variables(template_path):
    with open(template_path, 'r') as f:
        source = f.read()
    env = jinja2.Environment()
    ast = env.parse(source)
    return meta.find_undeclared_variables(ast)

def copy_templates_and_validate(service, vm_name):
    name = service["name"]
    role_path = ANSIBLE_ROLES_PATH / name
    role_templates_path = role_path / "templates"
    role_tasks_path = role_path / "tasks"
    template_source_path = TEMPLATES_PATH / name

    if not template_source_path.exists():
        print(f"❌ Error: No templates found for service '{name}' in {template_source_path}")
        return False

    role_templates_path.mkdir(parents=True, exist_ok=True)
    role_tasks_path.mkdir(parents=True, exist_ok=True)

    all_vars_found = True

    for file in template_source_path.iterdir():
        if file.name.endswith(".j2"):
            required_vars = extract_jinja_variables(file)

            # Prepare context for variable checking
            context = {
                **template_vars,
                **service,
                "service": service,
                "host": hosts.get(vm_name, {}),
            }

            missing_vars = [
                var for var in required_vars
                if var not in context and var not in KNOWN_ANSIBLE_VARS
            ]

            if missing_vars:
                print(f"❌ Error: Missing required variables in '{file.name}' for service '{name}': {missing_vars}")
                all_vars_found = False
                continue

            # Copy file to templates or tasks/main.yml
            if "main" in file.name:
                dest = role_tasks_path / "main.yml"
            else:
                dest = role_templates_path / file.name
            shutil.copyfile(file, dest)

    return all_vars_found

def generate_playbook_for_host(vm_name, services_for_host, base_dir=BASE_DIR):
    playbooks_dir = base_dir.parent / "ansible"
    playbooks_dir.mkdir(parents=True, exist_ok=True)

    playbook_blocks = []

    for service in services_for_host:
        name = service["name"]
        service_yaml = yaml.dump(service, default_flow_style=False, indent=4)
        service_yaml_indented = textwrap.indent(service_yaml, ' ' * 6)

        block = (
            f"- name: Run {name} on {vm_name}\n"
            f"  hosts: {vm_name}\n"
            f"  become: false\n"
            f"  gather_facts: true\n"
            f"  vars:\n"
            f"    service:\n"
            f"{service_yaml_indented}"
            f"  roles:\n"
            f"    - {name}\n"
        )
        playbook_blocks.append(block)

    playbook_content = "\n".join(playbook_blocks)
    playbook_path = playbooks_dir / f"{vm_name}.yml"

    with open(playbook_path, "w") as f:
        f.write(playbook_content)

    print(f"📄 Generated host playbook: {playbook_path}")

if __name__ == "__main__":
    config = load_config()
    services = config.get("services", [])
    hosts = {host["name"]: host for host in config.get("hosts", [])}
    template_vars = config.get("template", {}).get("ubuntu", {})

    services_by_vm = {}

    for service in services:
        vm_name = service["vm"]
        services_by_vm.setdefault(vm_name, []).append(service)

    for vm_name, services_for_host in services_by_vm.items():
        all_success = True
        for service in services_for_host:
            name = service["name"]

            if vm_name not in hosts:
                print(f"❌ Error: VM '{vm_name}' for service '{name}' not found in hosts config.")
                all_success = False
                continue

            success = copy_templates_and_validate(service, vm_name)
            if not success:
                print(f"⚠️  Role '{name}' was not fully generated for VM '{vm_name}'")
                all_success = False

        if all_success:
            print(f"✅ All roles successfully generated for VM '{vm_name}'")
            generate_playbook_for_host(vm_name, services_for_host)