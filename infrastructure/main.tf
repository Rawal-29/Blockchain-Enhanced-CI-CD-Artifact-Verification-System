
terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.15"
    }
  }
}


provider "kubernetes" {
  # Example: using environment variables set by a CI runner
  host                   = var.kubernetes_host
  client_certificate     = var.kubernetes_client_certificate
  client_key             = var.kubernetes_client_key
  cluster_ca_certificate = var.kubernetes_cluster_ca_certificate
}


module "app_deployment" {
  source = "./" 
  
  # Pass variables from the command line/CI/CD run to the module
  project_name         = var.project_name
  image_tag            = var.image_tag
  contract_address     = var.contract_address
  rpc_url              = var.rpc_url
  private_key_secret   = var.private_key_secret
}
