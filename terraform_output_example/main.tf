resource "proxmox_virtual_environment_vm" "vm-router" {
  name      = "vm-router"
  node_name = "lab-node"
  vm_id     = 9001

  clone {
    vm_id = 9000
    datastore_id = "default-datastore"
  }

  agent {
    enabled = false
  }

  cpu {
    cores = 2
  }

  memory {
    dedicated = 4096
  }

  disk {
    datastore_id = "default-datastore"
    interface = "virtio0"
    size = 32
  }

  initialization {
    datastore_id = "default-datastore"
    ip_config {
      ipv4 {
        address = "192.168.100.101/24"
        gateway = "192.168.100.1"
      }
    }
    user_account {
      username = "labadmin"
      keys     = [file("/home/user/.ssh/id_rsa_lab.pub")]
    }
  }

  network_device {
    bridge = "vmbr0"
  }
}

resource "proxmox_virtual_environment_vm" "vm-database" {
  name      = "vm-database"
  node_name = "lab-node"
  vm_id     = 9002

  clone {
    vm_id = 9000
    datastore_id = "default-datastore"
  }

  agent {
    enabled = false
  }

  cpu {
    cores = 4
  }

  memory {
    dedicated = 8192
  }

  disk {
    datastore_id = "default-datastore"
    interface = "virtio0"
    size = 64
  }

  initialization {
    datastore_id = "default-datastore"
    ip_config {
      ipv4 {
        address = "192.168.100.102/24"
        gateway = "192.168.100.1"
      }
    }
    user_account {
      username = "labadmin"
      keys     = [file("/home/user/.ssh/id_rsa_lab.pub")]
    }
  }

  network_device {
    bridge = "vmbr0"
  }
}