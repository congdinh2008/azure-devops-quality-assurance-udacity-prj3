# Udacity Nanodegree: Cloud DevOps using Microsoft Azure - Project 3: Ensuring Quality Releases

## Table of Contents

- [Udacity Nanodegree: Cloud DevOps using Microsoft Azure - Project 3: Ensuring Quality Releases](#udacity-nanodegree-cloud-devops-using-microsoft-azure---project-3-ensuring-quality-releases)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Getting Started](#getting-started)
  - [Dependencies](#dependencies)
  - [Instructions](#instructions)
    - [Login with Azure CLI - create a Service Principal Terraform](#login-with-azure-cli---create-a-service-principal-terraform)
    - [Configure the Storage Account and State Backend](#configure-the-storage-account-and-state-backend)
    - [Create Packer Image](#create-packer-image)
    - [Generate an SSH key pair and perform a keyscan to get the known hosts.](#generate-an-ssh-key-pair-and-perform-a-keyscan-to-get-the-known-hosts)
    - [\[OPTIONAL\] Run terraform on local](#optional-run-terraform-on-local)
    - [Create Azure Project, and configure Service Connection](#create-azure-project-and-configure-service-connection)
    - [Upload files to Azure DevOps Library Secure files](#upload-files-to-azure-devops-library-secure-files)
    - [Create a DevOps Pipeline](#create-a-devops-pipeline)
  - [Configure Azure Monitor](#configure-azure-monitor)
  - [Configure Azure Log Analytics Workspace](#configure-azure-log-analytics-workspace)
  - [Screenshots](#screenshots)

## Overview

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

### Login with Azure CLI - create a Service Principal Terraform

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

  ```bash
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

### Generate an SSH key pair and perform a keyscan to get the known hosts.

- Generate a public/private key pair locally as:

  ```bash
  ## Run in your local terminal
  ssh-keygen -t rsa
  cat ~/.ssh/id_rsa.pub
  ```

  After running the command above you will have a public SSH Key available at ~/.ssh/id_rsa.pub path.

- Perform keyscan

  ```bash
  ## Run in your local terminal
  ssh-keyscan github.com
  ```

- Swap comment the following line in terraform.tfvars if you want to run terraform on local

  ```bash
  # Azure
  public_key_path = "id_rsa.pub"

  # Local
  # public_key_path = "~/.ssh/id_rsa.pub"
  ```

### [OPTIONAL] Run terraform on local

- Go to terraform/environments/test
- Run the following command to import Resource Group if existed
  ```bash
  terraform import module.resource_group.azurerm_resource_group.test /subscriptions/fw37707e-577e-4bb6-93e2-7c09a6a2fbd3/resourceGroups/Azuredevops
  ```
- Terraform Init
  ```bash
  terraform init -backend-config=backend.conf
  ```
- Terraform Validate
  ```bash
  terraform validate
  ```
- Terraform Plan
  ```bash
  terraform plan -out solution.plan
  ```
- Terraform Apply
  ```bash
  terraform plan -out solution.plan
  ```
- Clean up
  ```bash
  terraform destroy
  ```

### Create Azure Project, and configure Service Connection

- Create Azure DevOps Project
  <img src="./screenshots/Create_Azure_DevOps_Project_01.png">

- Create Service Connection
  Project Settings > Service Connection > Add Service Connection
  <img src="./screenshots/Create_Service_Connection_Azure_DevOps_01.png">

- Install Azure DevOps Extension
  - [Terraform Extension](https://marketplace.visualstudio.com/items?itemName=ms-devlabs.custom-terraform-tasks&targetId=625be685-7d04-4b91-8e92-0a3f91f6c3ac&utm_source=vstsproduct&utm_medium=ExtHubManageList)

### Upload files to Azure DevOps Library Secure files

- Go to Azure DevOps Library
  Azure Project > Pipelines > Library > Secure files

- Select the below files to upload
  - terraform.tfvars
  - backend.conf
  - id_rsa.pub
  - id_rsa

  <img src="./screenshots/Pipeline_Library_Secure_Files.png">


### Create a DevOps Pipeline

- Modify the following lines on azure-pipelines.yaml:

  | Line # | parameter                        | description                              |
  | ------ | -------------------------------- | ---------------------------------------- |
  | 81     | knownHostsEntry                  | the knownHost of your ssh-keyscan github |
  | 82     | sshPublicKey                     | your public ssh key                      |
  | 102    | backendAzureRmResourceGroupName  | based on your storage account info       |
  | 103    | backendAzureRmStorageAccountName | based on your storage account info       |
  | 104    | backendAzureRmContainerName      | based on your storage account info       |
  | 105    | backendAzureRmKey                | based on your storage account info       |
  | 199    | azureSubscription                | Pipeline > Service Connections           |

- Navigate to the DevOps project, and select Pipeline and create a new one. You will use the following steps:

  - `Connect` - Choose the Github repository as the source code location.
    
    <img src="./screenshots/Pipeline_Choose_Connect.png">


  - `Select` - Select the Github repository containing the exercise starter code.

    <img src="./screenshots/Pipeline_Select_GitHub_Repository.png">

  - `Configure` - Choose the Existing Azure Pipelines YAML file option. When you do not have any starter YAML file already, you can choose Starter pipeline option, as shown in the snapshot below.

    <img src="./screenshots/Pipeline_Selected_Existing_Yaml_File.png">

  - `Edit and Review the azure-pipelines.yaml file` - Start with a minimal pipeline version and add more tasks/steps incrementally.
  
    <img src="./screenshots/Pipeline_Review_Or_Edit.png">

- Run the pipeline and wait for it to complete

  At the first time, you need to permit access to the Azure Pipelines Library secure files

  And after the pipeline completes provisioning stage. You need to add new resources to environment `test`

  Pipelines > Environment > test > Add resource > Virtual Machines > Next > Linux Operating system

  <img src="./screenshots/Pipeline_Environments_Register_VM_Script.png">

  Copy Registration script to run on created virtual machine

  - Connect to Azure Virtual Machine

  ```bash
  # Replace with your account in terraform.tfvars and VM IP address
  ssh account@20.24.18.81
  ```

  - Run Registration script

  script similar to the following example:

  ```bash
  mkdir azagent;cd azagent;curl -fkSL -o vstsagent.tar.gz https://vstsagentpackage.azureedge.net/agent/3.220.5/vsts-agent-linux-x64-3.220.5.tar.gz;tar -zxvf vstsagent.tar.gz; if [ -x "$(command -v systemctl)" ]; then ./config.sh --environment --environmentname "test" --acceptteeeula --agent $HOSTNAME --url https://dev.azure.com/your-organization/ --work _work --projectname 'udacity-project03' --auth PAT --token sfsnoraads4udh6yb3anzqasgzd6ocmyyus6p4v5b4fxa --runasservice; sudo ./svc.sh install; sudo ./svc.sh start; else ./config.sh --environment --environmentname "test" --acceptteeeula --agent $HOSTNAME --url https://dev.azure.com/your-organization/ --work _work --projectname 'udacity-project03' --auth PAT --token sfsnoraads4uwshrcnzqasgzd6ocmyyus6p4v5b4fxa; ./run.sh; fi
  ```

  <img src="./screenshots/Pipeline_Run_Summary_Stages.png">
  

## Configure Azure Monitor

- Go to the Azure Portal > Web App Services
 
  <img src="./screenshots/Web_App_Alerts.png">

- Create a new Alert in the "Monitoring" group

  <img src="./screenshots/Create_HTTP_404_Alert.png">

## Configure Azure Log Analytics Workspace

- Go to project directory
- Update resource group and name of the log analytics workspace in `create_log_analytics_workspace.sh` and `create_log_analytics_ws_template.json`
- Run script to create Log Analytics Workspace
  ```bash
  # Enter workspace name when creating log analytics workspace
  sh create_log_analytics_workspace.sh
  ```
  <img src="./screenshots/Log_Analytics_Workspace_Overview.png">
- Go to the Azure Portal > Log Analytics Workspace > Agents
  <img src="./screenshots/Log_Analytics_Workspace_Agents_Linux_Configuration.png">

- Enter to the VM by ssh
  ```bash
  # Replace with your account in terraform.tfvars and VM IP address
  ssh account@20.24.18.81
  ```
- Install the OSMAgent
  ```bash
  wget https://raw.githubusercontent.com/Microsoft/OMS-Agent-for-Linux/master/installer/scripts/onboard_agent.sh && sh onboard_agent.sh -w <YOUR WORKSPACE ID> -s <YOUR WORKSPACE PRIMARY KEY> -d opinsights.azure.com
  sudo /opt/microsoft/omsagent/bin/service_control restart <YOUR WORKSPACE ID>
  ```
- Wait a few minutes for the server to connect
  <img src="./screenshots/Log_Analytics_Workspace_Agents_Linux_Connected.png">
- Go to Log Analytics workspace > Settings > Tables
  
  <img src="./screenshots/Log_Analytics_Workspace_Tables_Custom_Log.png">

- Choose Create > New Custom Log (MMA-Based)

  <img src="./screenshots/Create_Custom_Log_01.png">

- You need to upload a sample log.

  <img src="./screenshots/Create_Custom_Log_02.png">

  <img src="./screenshots/Create_Custom_Log_03.png">
  
  <img src="./screenshots/Create_Custom_Log_04.png">
  
  <img src="./screenshots/Create_Custom_Log_05.png">

- Querying custom logs
  
  <img src="./screenshots/Selenium_query_custom_logs_table.png">  

## Screenshots
Link to the [Screenshots](https://github.com/congdinh2008/azure-devops-quality-assurance-udacity-prj3/tree/main/screenshots)