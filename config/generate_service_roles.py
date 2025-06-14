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
PLAYBOOKS_DIR = BASE_DIR.parent / "ansible"

KNOWN_ANSIBLE_VARS = {
    "ansible_user_dir",
    "ansible_user",
    "inventory_hostname",
    "ansible_hostname",
    "ansible_os_family",
    "ansible_distribution",
    "ansible_architecture",
    "ansible_facts",
    "ansible_env",
    "db_list",
    "db_name",
    "homelab_config",
    # add more as needed
}

def load_config():
    with CONFIG_PATH.open() as f:
        return yaml.safe_load(f)

def extract_jinja_variables(template_path):
    try:
        with open(template_path, 'r') as f:
            source = f.read()
        env = jinja2.Environment()
        ast = env.parse(source)
        return meta.find_undeclared_variables(ast)
    except jinja2.exceptions.TemplateSyntaxError as e:
        print(f"\n❌ TemplateSyntaxError in file: {template_path}")
        print(f"   → Line {e.lineno}: {e.message}")
        # Optional: show the line from the file for context
        try:
            lines = source.splitlines()
            if 0 < e.lineno <= len(lines):
                print(f"   → Content: {lines[e.lineno - 1]}")
        except Exception:
            pass
        raise  # re-raise to preserve stack trace

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

            context = {
                **template_vars,
                **service,
                "service": service,
                "host": hosts.get(vm_name, {}),
            }

            missing_vars = []

            for var in required_vars:
                if var in KNOWN_ANSIBLE_VARS:
                    continue
                if var in context:
                    continue
                if var.startswith("service."):
                    nested_key = var.split('.', 1)[1]
                    if nested_key in context.get("service", {}):
                        continue
                missing_vars.append(var)

            if missing_vars:
                print(f"❌ Error: Missing required variables in '{file.name}' for service '{name}': {missing_vars}")
                all_vars_found = False
                continue

            # Copy file to templates or tasks/main.yml
            if file.name == 'tasks_main.yml.j2':
                dest = role_tasks_path / "main.yml"
            else:
                dest = role_templates_path / file.name
            shutil.copyfile(file, dest)

    return all_vars_found

def generate_playbook_for_host(vm_name, services_for_host, base_dir=BASE_DIR):
    playbooks_dir = base_dir.parent / "ansible"
    playbooks_dir.mkdir(parents=True, exist_ok=True)

    playbook_blocks = []

    # Generate service role blocks
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

    # Write final playbook
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

    # --- New part: generate _05_deploy_services.yml in deploy order ---

    def get_deploy_order(vm_name):
        host = hosts.get(vm_name, {})
        return host.get("deploy_order", 9999)  # Default high number if missing

    ordered_vms = sorted(services_by_vm.keys(), key=get_deploy_order)

    deploy_playbook_path = PLAYBOOKS_DIR / "_05_deploy_services.yml"
    PLAYBOOKS_DIR.mkdir(parents=True, exist_ok=True)

    with open(deploy_playbook_path, "w") as f:
        f.write("---\n")
        for vm in ordered_vms:
            f.write(f"- import_playbook: {vm}.yml\n")

    print(f"✅ Generated deployment playbook: {deploy_playbook_path}")