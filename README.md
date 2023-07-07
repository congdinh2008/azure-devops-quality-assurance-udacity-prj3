# Udacity Nanodegree: Cloud DevOps using Microsoft Azure - Project 3: Ensuring Quality Releases

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Dependencies](#dependencies)
- [Instructions](#instructions)
  - [Login with Azure CLI](#login-with-azure-cli)
  - [Configure the storage account and state backend](#configure-the-storage-account-and-state-backend)
  - [Configuring Terraform](#configuring-terraform)
  - [Executing Terraform](#executing-terraform)
  - [Setting up Azure DevOps](#setting-up-azure-devops)
  - [Configuring the VM as a Resource](#configuring-the-vm-as-a-resource)
  - [Adding service connection](#adding-service-connection)
  - [Create a Service Principal for Terraform](#create-a-service-principal-for-terraform)
  - [Run the pipeline](#run-the-pipeline)
  - [Configure Azure Monitor](#configure-azure-monitor)
  - [Configure Azure Log Analytics](#configure-azure-log-analytics)
    - [Setting up custom logs](#setting-up-custom-logs)
    - [Querying custom logs](#querying-custom-logs)
- [Clean-up](#clean-up)
- [Screenshots](#screenshots)
  - [Environment creation & deployment](#environment-creation--deployment)
    - [Terraform](#terraform)
    - [Azure Pipeline](#azure-pipeline)
  - [Automated testing](#automated-testing)
    - [Postman](#postman)
    - [Selenium](#selenium)
    - [JMeter](#jmeter)
  - [Monitoring & observability](#monitoring--observability)
    - [Azure Monitor](#azure-monitor)
    - [Azure Log Analytics](#azure-log-analytics)
- [References](#references)
- [Requirements](#requirements)
- [License](#license)

## Overview

### Ensuring Quality Releases - Project Overview

In this project, you'll develop and demonstrate your skills in using a variety of industry leading tools, especially Microsoft Azure, to create disposable test environments and run a variety of automated tests with the click of a button. Additionally, you'll monitor and provide insight into your application's behavior, and determine root causes by querying the application’s custom log files.

<img src="./screenshots/intro.png">

## Getting Started

    1. Fork this repository
    2. Ensure you have all the dependencies
    3. Follow the instructions below

## Dependencies

| Dependency           | Link                                                                            |
| -------------------- | ------------------------------------------------------------------------------- |
| Azure Account        | https://portal.azure.com/                                                       |
| Azure DevOps Account | https://azure.microsoft.com/en-us/pricing/details/devops/azure-devops-services/ |
| Azure CLI            | https://learn.microsoft.com/en-us/cli/azure/install-azure-cli                   |
| Packer               | https://developer.hashicorp.com/packer/downloads?product_intent=packer          |
| Terraform            | https://www.terraform.io/downloads.html                                         |
| JMeter               | https://jmeter.apache.org/download_jmeter.cgi                                   |
| Postman              | https://www.postman.com/downloads/                                              |
| Python               | https://www.python.org/downloads/                                               |
| Selenium             | https://sites.google.com/a/chromium.org/chromedriver/getting-started            |

## Instructions

### Login Azure Account with Azure CLI - create a Service Principal for Terraform.

- Firstly, login to the Azure CLI using::

  ```bash
  az login
  ```

- Once logged in - it's possible to list the Subscriptions associated with the account via:
  ```bash
  az account list
  ```
  The output (similar to below) will display one or more Subscriptions - with the id field being the subscription_id field referenced above.
  ```bash
  [
      {
          "cloudName": "AzureCloud",
          "id": "20000000-0000-0000-0000-000000000000",
          "isDefault": true,
          "name": "PAYG Subscription",
          "state": "Enabled",
          "tenantId": "10000000-0000-0000-0000-000000000000",
          "user": {
          "name": "user@example.com",
          "type": "user"
          }
      }
  ]
  ```
- Should you have more than one Subscription, you can specify the Subscription to use via the following command:

  ```bash
  az account set --subscription="20000000-0000-0000-0000-000000000000"
  ```

- We can now create the Service Principal which will have permissions to manage resources in the specified Subscription using the following command:
  ```bash
  az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/20000000-0000-0000-0000-000000000000"
  ```
  This command will output 5 values:
  ```bash
  {
      "appId": "00000000-0000-0000-0000-000000000000",
      "displayName": "azure-cli-2017-06-05-10-41-15",
      "name": "http://azure-cli-2017-06-05-10-41-15",
      "password": "0000-0000-0000-0000-000000000000",
      "tenant": "00000000-0000-0000-0000-000000000000"
  }
  ```
- Update terraform/environments/test/terraform.tfvars
    
    Rename `terraform.tfvars.example` to `terraform.tfvars`
    Replace the subscription variable values in the terraform.tfvars file, as applicable to you: 
    ```
    subscription_id = "0b72aa91-69d1-4842-8da0-1dbc098c1665"
    client_id = "53149600-f56a-41bd-8416-16ff00085351"
    client_secret = "Yw-8Q~xqgTGNb5UypephtTtfFPyEJ~kBtob5Gco5"
    tenant_id = "f958e84a-92b8-439f-a62d-4f45996b6d07"
    ```

    Verify/update the Resource Group, Location, Network, VM and public key path variables in the terraform.tfvars file:

    ```
    # Resource Group/Location
    location         = "Southeast Asia"
    resource_group   = "Azuredevops"
    application_type = "WebApplication"

    # Network
    virtual_network_name = "udacity-project03-vnet"
    address_space        = ["10.5.0.0/16"]
    address_prefix_test  = "10.5.1.0/24"

    # VM
    vm_size           = "Standard_B1s"
    vm_admin_username = "congdinh"
    packer_image_name = "udacity-ubuntu-server-image"

    # Azure
    public_key_path = "id_rsa.pub"
    ```
### Configure the Storage Account and State Backend

Configure the storage account and state backend for Terraform to save its state when run as a part of the CI/CD pipeline later. Here are the commands for Mac/Linux users:

- Run script to config Storage Account

    ```bash
    ## For Mac/Linux
    cd terraform/environments/test

    chmod +x configure-tfstate-storage-account.sh
    ./configure-tfstate-storage-account.sh
    ```

- Update terraform/environments/test/backend.conf

    Rename `backend.conf.examples` to `backend.conf`
    Replace the value below with the output from the above information
    ``` bash
    storage_account_name = "tfstate123456789"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
    access_key           = "tePNuKEU/4hpuFI0dAea6vJF4XpDmxlp+jG3iXYy4ZRs6jIfa5hkWxWNVHa9YQrGHH/AECVhxftM+AStFzX2EQ=="
    ```
### Create Packer Image
- Go to the packer directory
    ```bash
    cd packer
    ```
- Export az authentication credentials
    ```bash
    ## Run on terminal - Replace with your account info
    export AZ_SUBSCRIPTION_ID=fc07707e-523e-4bb6-93e2-7c09a6a2fbd3
    export AZ_TENANT_ID=cd253f18-4b02-4f2f-b7b5-ac6ae67385d4
    export AZ_CLIENT_ID=a9cdfd8f-5412-4927-a103-e47727b29b62
    export AZ_CLIENT_SECRET=K4r8Q~aS9LH1ngM4.0dszKui4zF~FQ7pfMKsobZg
    ```
- Packer image
    ```bash
    packer build packer-image.json
    ```
### Generate an SSH key pair

- Generate a public/private key pair locally as:
    
    ```bash
    ## Run in your local terminal
    ssh-keygen -t rsa
    cat ~/.ssh/id_rsa.pub
    ```
    After running the command above you will have a public SSH Key available at ~/.ssh/id_rsa.pub path.

### Create Azure Project, and configure Service Connection
- Create Azure DevOps Project

- Create Service Connection
    Project Settings > Service Connection > Add Service Connection
- Install Azure DevOps Extension
    + [Terraform Extension](https://marketplace.visualstudio.com/items?itemName=ms-devlabs.custom-terraform-tasks&targetId=625be685-7d04-4b91-8e92-0a3f91f6c3ac&utm_source=vstsproduct&utm_medium=ExtHubManageList)

### Upload files to Azure DevOps Library Secure files
- Go to Azure DevOps Library
    Azure Project > Pipelines > Library > Secure files

- Select the below files to upload
    + terraform.tfvars
    + backend.conf
    + id_rsa.pub
    + id_rsa

### Create a DevOps Pipeline

- Navigate to the DevOps project, and select Pipeline and create a new one. You will use the following steps:

    + `Connect` - Choose the Github repository as the source code location.

    + `Select` - Select the Github repository containing the exercise starter code.
    
    + `Configure` - Choose the Existing Azure Pipelines YAML file option. When you do not have any starter YAML file already, you can choose Starter pipeline option, as shown in the snapshot below.

    + `Edit and Review the azure-pipelines.yaml file` - Start with a minimal pipeline version and add more tasks/steps incrementally.


