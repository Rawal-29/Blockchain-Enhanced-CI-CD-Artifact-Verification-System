# infrastructure/openshift.tf

# NOTE: Assumes you have configured the OpenShift Provider in main.tf

# 1. OpenShift Namespace/Project
resource "kubernetes_namespace" "app_namespace" {
  metadata {
    name = var.project_name
  }
}

# 2. Secret for the Deployer Private Key
# The PRIVATE_KEY will be injected into this Terraform run via a CI secret manager
resource "kubernetes_secret" "verifier_secret" {
  metadata {
    name      = "verifier-secrets"
    namespace = kubernetes_namespace.app_namespace.metadata.0.name
  }
  data = {
    # CRITICAL: This value must be injected from a Gitlab/GitHub/Vault Secret
    DEPLOYER_PRIVATE_KEY = var.private_key_secret 
  }
  type = "Opaque"
}

# 3. OpenShift Deployment for the FastAPI App
resource "kubernetes_deployment" "verifier_deployment" {
  metadata {
    name      = "verifier-app"
    namespace = kubernetes_namespace.app_namespace.metadata.0.name
    labels = {
      App = "verifier-app"
    }
  }

  spec {
    replicas = 2
    selector {
      match_labels = {
        App = "verifier-app"
      }
    }
    template {
      metadata {
        labels = {
          App = "verifier-app"
        }
      }
      spec {
        container {
          name  = "verifier-container"
          image = "your-docker-registry/verifier-app:${var.image_tag}" # Replace with your registry URL

          port {
            container_port = 8000
          }

          # Inject configuration variables
          env {
            name  = "ETHEREUM_RPC_URL"
            value = var.rpc_url
          }
          env {
            name  = "CONTRACT_ADDRESS"
            value = var.contract_address
          }

          # Inject the sensitive private key from the Kubernetes Secret
          env {
            name = "DEPLOYER_PRIVATE_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.verifier_secret.metadata.0.name
                key  = "DEPLOYER_PRIVATE_KEY"
              }
            }
          }
        }
      }
    }
  }
}