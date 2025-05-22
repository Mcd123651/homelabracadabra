resource "proxmox_virtual_environment_vm" "ubuntu_template" {
  name      = "ubuntu-cloudinit-template"
  node_name = "lab-node"
  vm_id     = "9000"

  template = true
  started  = false

  machine     = "q35"
  description = "Managed by Terraform"

  agent {
    enabled = false
  }

  cpu {
    cores = 2
  }

  memory {
    dedicated = 1024
  }

  disk {
    datastore_id = "default-datastore"
    file_id      = proxmox_virtual_environment_download_file.ubuntu_cloud_image.id
    interface    = "virtio0"
    iothread     = true
    discard      = "on"
    size         = 20
  }

  initialization {
    datastore_id = "default-datastore"
    user_account {
      username = "labadmin"
      keys     = [file("/home/user/.ssh/id_rsa_lab.pub")]
    }
    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  network_device {
    bridge = "vmbr0"
  }
}

resource "proxmox_virtual_environment_download_file" "ubuntu_cloud_image" {
  content_type = "iso"
  datastore_id = "local"
  node_name    = "lab-node"

  url = "https://cloud-images.ubuntu.com/noble/current/ubuntu-cloudimg-amd64.img"
}