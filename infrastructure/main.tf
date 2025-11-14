# infrastructure/main.tf

# --- Providers Configuration ---
# You need to configure the provider that interacts with your OpenShift cluster.
# This often involves authenticating using service accounts or Kubeconfig files
# provided by your CI/CD runner.

terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.15"
    }
    # Add other providers here (e.g., local, external, random)
  }
}

# Configure the Kubernetes Provider
# The details for the host, client_certificate, etc., are usually provided
# by the CI/CD environment or a dedicated Kubeconfig file.
provider "kubernetes" {
  # Example: using environment variables set by a CI runner
  host                   = var.kubernetes_host
  client_certificate     = var.kubernetes_client_certificate
  client_key             = var.kubernetes_client_key
  cluster_ca_certificate = var.kubernetes_cluster_ca_certificate
}

# --- Modules ---
# Calls the openshift.tf deployment file
module "app_deployment" {
  source = "./" # Current directory, referencing openshift.tf
  
  # Pass variables from the command line/CI/CD run to the module
  project_name         = var.project_name
  image_tag            = var.image_tag
  contract_address     = var.contract_address
  rpc_url              = var.rpc_url
  private_key_secret   = var.private_key_secret
}
