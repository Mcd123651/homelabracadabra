import os
import yaml
from pathlib import Path

def resolve_ssh_key_path(path):
    return str(Path(path).expanduser())

def load_config(yml_path):
    with open(yml_path, "r") as f:
        return yaml.safe_load(f)

def build_vm_shell_function(vm, target_node):
    ssh_key_path = resolve_ssh_key_path(vm["ssh_pub_key_path"])
    vmid = vm["vmid"]

    name = vm["name"]
    memory = vm["memory"]
    cores = vm["cores"]
    disk = f"{vm['disk']}G"
    ip = vm["ip"]
    gateway = vm["gateway"]
    template = vm["template"]

    # Escape $ and braces for bash variables inside Python f-string:
    return f"""
configure_vm_{vmid}() {{
    local vmid={vmid}
    local name="{name}"
    local target_node="{target_node}"
    local template="{template}"
    local memory={memory}
    local cores={cores}
    local disk="{disk}"
    local ip="{ip}"
    local gateway="{gateway}"
    local ssh_key_file="{ssh_key_path}"

    # Check if VM exists
    if ! qm status ${{vmid}} &>/dev/null; then
        echo "VM ${{vmid}} does not exist. Creating..."
        qm clone ${{template}} ${{vmid}} --name ${{name}} --full true --node ${{target_node}}
        qm set ${{vmid}} --memory ${{memory}} --cores ${{cores}} --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci --scsi0 local-zfs:${{disk}}
        qm set ${{vmid}} --ipconfig0 ip=${{ip}}/24,gw=${{gateway}}
        qm set ${{vmid}} --sshkey "$(cat ${{ssh_key_file}})"
        qm start ${{vmid}}
        return
    fi

    # VM exists, check if running
    status=$(qm status ${{vmid}} | awk '{{print $2}}')
    echo "VM ${{vmid}} exists and is ${{status}}"

    # Get current config for comparison
    config=$(qm config ${{vmid}})

    # Helper function to extract value from qm config
    get_config_value() {{
        echo "$config" | grep "^$1:" | awk '{{print $2}}'
    }}

    current_memory=$(get_config_value "memory")
    current_cores=$(get_config_value "cores")
    current_net0=$(get_config_value "net0")
    current_scsi0=$(get_config_value "scsi0")
    current_ipconfig0=$(get_config_value "ipconfig0")
    current_sshkey_path="/tmp/sshkey_${{vmid}}.pub"

    # Compare and update if necessary

    if [ "$current_memory" != "$memory" ]; then
        echo "Updating memory for VM ${{vmid}} from $current_memory to $memory"
        qm set ${{vmid}} --memory $memory
    fi

    if [ "$current_cores" != "$cores" ]; then
        echo "Updating cores for VM ${{vmid}} from $current_cores to $cores"
        qm set ${{vmid}} --cores $cores
    fi

    if [[ "$current_net0" != "virtio,bridge=vmbr0" ]]; then
        echo "Updating network interface for VM ${{vmid}}"
        qm set ${{vmid}} --net0 virtio,bridge=vmbr0
    fi

    if [[ "$current_scsi0" != "local-zfs:${{disk}}" ]]; then
        echo "Disk size or storage differs for VM ${{vmid}}. Current: $current_scsi0, Desired: local-zfs:${{disk}}"
        # qm resize ${{vmid}} scsi0 {vm['disk']}G  # Uncomment carefully if needed
    fi

    if [[ "$current_ipconfig0" != "ip=${{ip}}/24,gw=${{gateway}}" ]]; then
        echo "Updating IP config for VM ${{vmid}}"
        qm set ${{vmid}} --ipconfig0 ip=${{ip}}/24,gw=${{gateway}}
    fi

    cat "$ssh_key_file" > "$current_sshkey_path"
    current_sshkey_content=$(qm config ${{vmid}} | grep ssh-keys | awk '{{ $1=""; print $0 }}' | xargs)
    new_sshkey_content=$(cat "$current_sshkey_path" | tr -d '\\n')

    if [[ "$current_sshkey_content" != "$new_sshkey_content" ]]; then
        echo "Updating SSH key for VM ${{vmid}}"
        qm set ${{vmid}} --sshkey "$new_sshkey_content"
    fi

    if [ "$status" != "running" ]; then
        echo "Starting VM ${{vmid}}"
        qm start ${{vmid}}
    fi
}}
"""

def write_shell_script(functions, vmids, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure scripts/ exists
    with open(output_path, "w") as f:
        f.write("#!/bin/bash\n\nset -e\n\n")
        for func in functions:
            f.write(func)
            f.write("\n\n")

        f.write("main() {\n")
        for vmid in vmids:
            f.write(f"  configure_vm_{vmid}\n")
        f.write("}\n\nmain\n")

    os.chmod(output_path, 0o755)
    print(f"✅ Shell script with VM checks generated: {output_path}")

def main():
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / "config" / "homelab.yml"
    output_path = base_dir / "scripts" / "create_vms_checked.sh"  # Save in scripts/

    config = load_config(config_path)
    target_node = config.get("proxmox", {}).get("target_node", "homelab")
    vms = config.get("vms", [])

    functions = []
    vmids = []
    for vm in vms:
        functions.append(build_vm_shell_function(vm, target_node))
        vmids.append(vm["vmid"])

    write_shell_script(functions, vmids, output_path)

if __name__ == "__main__":
    main()
