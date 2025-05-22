🡐[🧙‍♂️ homelabracadabra](../README.md)

# 🔧 Prerequisite for Teraform VM Setup

This guide will walk you through setting up your orchatration and variables for creating VMs in Proxmox.

1. [Raspberry PI](./PI4-README.md) (or similar linux based controller installed) to ensure Terraform and Keygens are installed.

---


## Create the Ubuntu Cloud-Init Template on Proxmox

In Proxmox goto Homelab -> Shell -> Log into root

```bash
#!/bin/bash

set -e

TEMPLATE_NAME="ubuntu-2404-cloudinit-template"
TEMPLATE_IMAGE="noble-server-cloudimg-amd64.img"
TEMPLATE_PATH="/var/lib/vz/template/${TEMPLATE_IMAGE}"
VMID=9000

# 1. Download and prepare image
wget -nc https://cloud-images.ubuntu.com/noble/current/${TEMPLATE_IMAGE}
qemu-img resize ${TEMPLATE_IMAGE} 32G
mv -n ${TEMPLATE_IMAGE} ${TEMPLATE_PATH}

# 2. Create base VM
qm create $VMID --name "$TEMPLATE_NAME" --ostype l26 \
  --memory 1024 \
  --agent 1 \
  --bios ovmf --machine q35 --efidisk0 local-zfs:0,pre-enrolled-keys=0 \
  --cpu host --socket 1 --cores 1 \
  --vga serial0 --serial0 socket \
  --net0 virtio,bridge=vmbr0

# 3. Import disk and attach cloud-init
qm importdisk $VMID $TEMPLATE_PATH local-zfs
qm set $VMID --scsihw virtio-scsi-pci --virtio0 local-zfs:vm-${VMID}-disk-0,discard=on
qm set $VMID --boot order=virtio0
qm set $VMID --scsi1 local-zfs:cloudinit

# 4. Setup cloud-init snippet
mkdir -p /var/lib/vz/snippets
cat <<EOF | tee /var/lib/vz/snippets/vendor.yaml
runcmd:
  - apt update
  - apt install -y qemu-guest-agent
  - systemctl start qemu-guest-agent
EOF

qm set $VMID --cicustom "vendor=local:snippets/vendor.yaml"
qm set $VMID --tags cloudinit,ubuntu-template,2404
qm set $VMID --ciuser homelab
qm set $VMID --ipconfig0 ip=dhcp

# 5. Convert to template
qm template $VMID
```