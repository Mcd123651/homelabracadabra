import yaml
from pathlib import Path

TEMPLATE_SCRIPT = """#!/bin/bash

set -e

TEMPLATE_NAME="{name}"
TEMPLATE_IMAGE="{image}"
TEMPLATE_PATH="/var/lib/vz/template/${{TEMPLATE_IMAGE}}"
VMID={vmid}

# 1. Download and prepare image
wget -nc https://cloud-images.ubuntu.com/noble/current/${{TEMPLATE_IMAGE}}
qemu-img resize ${{TEMPLATE_IMAGE}} 32G
mv -n ${{TEMPLATE_IMAGE}} ${{TEMPLATE_PATH}}

# 2. Create base VM
qm create ${{VMID}} --name "$TEMPLATE_NAME" --ostype l26 \\
  --memory {memory} \\
  --agent 1 \\
  --bios ovmf --machine q35 --efidisk0 local-zfs:0,pre-enrolled-keys=0 \\
  --cpu host --socket 1 --cores 1 \\
  --vga serial0 --serial0 socket \\
  --net0 virtio,bridge=vmbr0

# 3. Import disk and attach cloud-init
qm importdisk ${{VMID}} ${{TEMPLATE_PATH}} local-zfs
qm set ${{VMID}} --scsihw virtio-scsi-pci --virtio0 local-zfs:vm-${{VMID}}-disk-1,discard=on
qm set ${{VMID}} --boot order=virtio0
qm set ${{VMID}} --scsi1 local-zfs:cloudinit

# 4. Setup cloud-init snippet
mkdir -p /var/lib/vz/snippets
cat <<EOF | tee /var/lib/vz/snippets/vendor.yaml
runcmd:
  - apt update
  - apt install -y qemu-guest-agent
  - systemctl start qemu-guest-agent
EOF

qm set ${{VMID}} --cicustom "vendor=local:snippets/vendor.yaml"
qm set ${{VMID}} --tags {tags}
qm set ${{VMID}} --ciuser {user}
qm set ${{VMID}} --ipconfig0 ip=dhcp

# 5. Convert to template
qm template ${{VMID}}
"""

def load_template_config(yml_path):
    with open(yml_path, "r") as f:
        config = yaml.safe_load(f)
        return config.get("template", {})

def generate_script(template_config, output_path):
    tags = ",".join(template_config.get("tags", []))
    script_content = TEMPLATE_SCRIPT.format(
        name=template_config["name"],
        image=template_config["image"],
        vmid=template_config["vmid"],
        memory=template_config["memory"],
        user=template_config["user"],
        tags=tags
    )
    with open(output_path, "w") as f:
        f.write(script_content)
    Path(output_path).chmod(0o755)
    print(f"✅ Script written to {output_path}")

def main():
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / "config" / "homelab.yml"
    output_path = base_dir / "scripts" / "create_cloudinit_template.sh"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    template_config = load_template_config(config_path)
    if not template_config:
        print("❌ No 'template' config found in homelab.yml.")
        return

    generate_script(template_config, output_path)

if __name__ == "__main__":
    main()
