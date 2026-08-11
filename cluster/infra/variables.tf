variable "ssh_public_key" {
  type        = string
  description = "SSH public Key for admin user"
}

variable "name" {
  description = "Project name"
  type        = string
  default     = "bbs-calib"
}

variable "ssh_port" {
  description = "SSH port"
  type        = number
  default     = 50022
}

variable "location" {
  description = "The server location"
  type        = string
}

variable "ssh_allowed_ips" {
  type        = list(string)
  description = "IP Addresses allowed to connect to the SSH port"
  default     = ["0.0.0.0/0", "::/0"]
}

variable "hcloud_token" {
  type        = string
  description = "Hetzner Cloud API token"
  sensitive   = true
}

variable "instance_type" {
  type        = string
  description = "Hetzner Cloud instance type"
  default     = "cpx62"
}

variable "instance_count" {
  type        = number
  description = "Number of instances to create"
  default     = 1
}
