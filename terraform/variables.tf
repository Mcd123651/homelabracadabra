
variable "pm_api_url" {
  description = "Proxmox API URL"
  type        = string
  default     = "https://10.11.30.4:8006/api2/json"
}

variable "pm_user" {
  description = "Proxmox username"
  type        = string
  default     = "root@pam"
}

variable "pm_password" {
  description = "Proxmox password"
  type        = string
  sensitive   = true
}

variable "pm_tls_insecure" {
  description = "Allow insecure TLS connections"
  type        = bool
  default     = true
}

variable "default_password" {
  description = "Default password for VM users"
  type        = string
  sensitive   = true
}

variable "virtual_environment_token" {
  type        = string
  description = "The token for the Proxmox Virtual Environment API"
  sensitive   = true
}