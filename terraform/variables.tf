variable "project_id" {
  description = "ID du projet Google Cloud"
  type        = string
}

variable "region" {
  description = "Région GCP"
  type        = string
  default     = "europe-west9" # Paris
}

variable "zone" {
  description = "Zone GCP"
  type        = string
  default     = "europe-west9-b"
}

variable "machine_type" {
  description = "Type de machine Compute Engine"
  type        = string
  default     = "e2-small"
}

variable "ssh_user" {
  description = "Utilisateur SSH pour le déploiement"
  type        = string
  default     = "deploy"
}

variable "ssh_pub_key_path" {
  description = "Chemin vers la clé publique SSH"
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}
