resource "azurerm_network_interface" "test" {
  name                = "${var.application_type}-${var.resource_type}-nic"
  location            = var.location
  resource_group_name = var.resource_group

  ip_configuration {
    name                          = "internal"
    subnet_id                     = var.subnet_id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = var.public_ip_address_id
  }
}

data "azurerm_image" "packer-image" {
  name                = var.packer_image_name
  resource_group_name = var.resource_group
}

resource "azurerm_linux_virtual_machine" "test" {
  name                            = "${var.application_type}-${var.resource_type}-vm"
  location                        = var.location
  resource_group_name             = var.resource_group
  size                            = var.vm_size
  source_image_id                 = data.azurerm_image.packer-image.id
  admin_username                  = var.vm_admin_username
  disable_password_authentication = true

  network_interface_ids = [azurerm_network_interface.test.id]

  admin_ssh_key {
    username   = var.vm_admin_username
    public_key = file(var.public_key_path)
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }
}
