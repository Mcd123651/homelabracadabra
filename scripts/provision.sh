#!/bin/bash

set -e

echo "🔐 Exporting secrets from terraform.tfvars..."
export TF_VAR_pm_password=$(jq -r '.pm_password' terraform/terraform.tfvars)
export TF_VAR_default_password=$(jq -r '.default_password' terraform/terraform.tfvars)

echo "🚀 Running Terraform to provision VMs..."
cd terraform
terraform init
terraform apply -auto-approve
cd ..

# SSH setup (optional Pi4 SSH into VMs)
# ssh-copy-id -i ~/.ssh/id_rsa.pub homelab@VM_IP
# Example:
# ssh homelab@192.168.1.101


# (Ansible step skipped)

# Optional: Docker setup on VMs
# ssh homelab@VM_IP 'bash -s' < setup-docker.sh


echo "✅ Homelab provisioning complete."
