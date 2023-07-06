# Common
variable "location" {}
variable "resource_group" {}
variable "resource_type" {}
variable "application_type" {}

# NIC
variable "subnet_id" {}
variable "public_ip_address_id" {}

# VM
variable "vm_size" {}
variable "vm_admin_username" {}
variable "packer_image_name" {}
variable "public_key_path" {}
