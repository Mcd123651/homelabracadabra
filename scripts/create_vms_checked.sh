#!/bin/bash

set -e


configure_vm_1001() {
    local vmid=1001
    local name="vm-networking"
    local target_node="homelab"
    local template="ubuntu-2404-cloudinit-template"
    local memory=4096
    local cores=2
    local disk="32GG"
    local ip="10.11.30.6/24"
    local gateway="10.11.30.1"
    local ssh_key_file="/home/pi/.ssh/id_rsa_homelab.pub"

    # Check if VM exists
    if ! qm status ${vmid} &>/dev/null; then
        echo "VM ${vmid} does not exist. Creating..."
        qm clone ${template} ${vmid} --name ${name} --full true --node ${target_node}
        qm set ${vmid} --memory ${memory} --cores ${cores} --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci --scsi0 local-zfs:${disk}
        qm set ${vmid} --ipconfig0 ip=${ip}/24,gw=${gateway}
        qm set ${vmid} --sshkey "$(cat ${ssh_key_file})"
        qm start ${vmid}
        return
    fi

    # VM exists, check if running
    status=$(qm status ${vmid} | awk '{print $2}')
    echo "VM ${vmid} exists and is ${status}"

    # Get current config for comparison
    config=$(qm config ${vmid})

    # Helper function to extract value from qm config
    get_config_value() {
        echo "$config" | grep "^$1:" | awk '{print $2}'
    }

    current_memory=$(get_config_value "memory")
    current_cores=$(get_config_value "cores")
    current_net0=$(get_config_value "net0")
    current_scsi0=$(get_config_value "scsi0")
    current_ipconfig0=$(get_config_value "ipconfig0")
    current_sshkey_path="/tmp/sshkey_${vmid}.pub"

    # Compare and update if necessary

    if [ "$current_memory" != "$memory" ]; then
        echo "Updating memory for VM ${vmid} from $current_memory to $memory"
        qm set ${vmid} --memory $memory
    fi

    if [ "$current_cores" != "$cores" ]; then
        echo "Updating cores for VM ${vmid} from $current_cores to $cores"
        qm set ${vmid} --cores $cores
    fi

    if [[ "$current_net0" != "virtio,bridge=vmbr0" ]]; then
        echo "Updating network interface for VM ${vmid}"
        qm set ${vmid} --net0 virtio,bridge=vmbr0
    fi

    if [[ "$current_scsi0" != "local-zfs:${disk}" ]]; then
        echo "Disk size or storage differs for VM ${vmid}. Current: $current_scsi0, Desired: local-zfs:${disk}"
        # qm resize ${vmid} scsi0 32GG  # Uncomment carefully if needed
    fi

    if [[ "$current_ipconfig0" != "ip=${ip}/24,gw=${gateway}" ]]; then
        echo "Updating IP config for VM ${vmid}"
        qm set ${vmid} --ipconfig0 ip=${ip}/24,gw=${gateway}
    fi

    cat "$ssh_key_file" > "$current_sshkey_path"
    current_sshkey_content=$(qm config ${vmid} | grep ssh-keys | awk '{ $1=""; print $0 }' | xargs)
    new_sshkey_content=$(cat "$current_sshkey_path" | tr -d '\n')

    if [[ "$current_sshkey_content" != "$new_sshkey_content" ]]; then
        echo "Updating SSH key for VM ${vmid}"
        qm set ${vmid} --sshkey "$new_sshkey_content"
    fi

    if [ "$status" != "running" ]; then
        echo "Starting VM ${vmid}"
        qm start ${vmid}
    fi
}



configure_vm_1002() {
    local vmid=1002
    local name="vm-databases"
    local target_node="homelab"
    local template="ubuntu-2404-cloudinit-template"
    local memory=8192
    local cores=4
    local disk="64GG"
    local ip="10.11.30.7/24"
    local gateway="10.11.30.1"
    local ssh_key_file="/home/pi/.ssh/id_rsa_homelab.pub"

    # Check if VM exists
    if ! qm status ${vmid} &>/dev/null; then
        echo "VM ${vmid} does not exist. Creating..."
        qm clone ${template} ${vmid} --name ${name} --full true --node ${target_node}
        qm set ${vmid} --memory ${memory} --cores ${cores} --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci --scsi0 local-zfs:${disk}
        qm set ${vmid} --ipconfig0 ip=${ip}/24,gw=${gateway}
        qm set ${vmid} --sshkey "$(cat ${ssh_key_file})"
        qm start ${vmid}
        return
    fi

    # VM exists, check if running
    status=$(qm status ${vmid} | awk '{print $2}')
    echo "VM ${vmid} exists and is ${status}"

    # Get current config for comparison
    config=$(qm config ${vmid})

    # Helper function to extract value from qm config
    get_config_value() {
        echo "$config" | grep "^$1:" | awk '{print $2}'
    }

    current_memory=$(get_config_value "memory")
    current_cores=$(get_config_value "cores")
    current_net0=$(get_config_value "net0")
    current_scsi0=$(get_config_value "scsi0")
    current_ipconfig0=$(get_config_value "ipconfig0")
    current_sshkey_path="/tmp/sshkey_${vmid}.pub"

    # Compare and update if necessary

    if [ "$current_memory" != "$memory" ]; then
        echo "Updating memory for VM ${vmid} from $current_memory to $memory"
        qm set ${vmid} --memory $memory
    fi

    if [ "$current_cores" != "$cores" ]; then
        echo "Updating cores for VM ${vmid} from $current_cores to $cores"
        qm set ${vmid} --cores $cores
    fi

    if [[ "$current_net0" != "virtio,bridge=vmbr0" ]]; then
        echo "Updating network interface for VM ${vmid}"
        qm set ${vmid} --net0 virtio,bridge=vmbr0
    fi

    if [[ "$current_scsi0" != "local-zfs:${disk}" ]]; then
        echo "Disk size or storage differs for VM ${vmid}. Current: $current_scsi0, Desired: local-zfs:${disk}"
        # qm resize ${vmid} scsi0 64GG  # Uncomment carefully if needed
    fi

    if [[ "$current_ipconfig0" != "ip=${ip}/24,gw=${gateway}" ]]; then
        echo "Updating IP config for VM ${vmid}"
        qm set ${vmid} --ipconfig0 ip=${ip}/24,gw=${gateway}
    fi

    cat "$ssh_key_file" > "$current_sshkey_path"
    current_sshkey_content=$(qm config ${vmid} | grep ssh-keys | awk '{ $1=""; print $0 }' | xargs)
    new_sshkey_content=$(cat "$current_sshkey_path" | tr -d '\n')

    if [[ "$current_sshkey_content" != "$new_sshkey_content" ]]; then
        echo "Updating SSH key for VM ${vmid}"
        qm set ${vmid} --sshkey "$new_sshkey_content"
    fi

    if [ "$status" != "running" ]; then
        echo "Starting VM ${vmid}"
        qm start ${vmid}
    fi
}


main() {
  configure_vm_1001
  configure_vm_1002
}

main
