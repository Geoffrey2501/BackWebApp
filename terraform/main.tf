terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# ── IP statique ──────────────────────────────────────────
resource "google_compute_address" "toyboxing" {
  name   = "toyboxing-ip"
  region = var.region
}

# ── Firewall : HTTP, HTTPS, SSH ──────────────────────────
resource "google_compute_firewall" "toyboxing" {
  name    = "toyboxing-allow-web"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22", "80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["toyboxing"]
}

# ── VM ───────────────────────────────────────────────────
resource "google_compute_instance" "toyboxing" {
  name         = "toyboxing"
  machine_type = var.machine_type
  zone         = var.zone

  tags = ["toyboxing"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size  = 20
    }
  }

  network_interface {
    network = "default"
    access_config {
      nat_ip = google_compute_address.toyboxing.address
    }
  }

  metadata = {
    ssh-keys = "${var.ssh_user}:${file(pathexpand(var.ssh_pub_key_path))}"
  }

  # Script de démarrage : installe Docker + Compose
  metadata_startup_script = <<-EOT
    #!/bin/bash
    set -e

    # Docker
    if ! command -v docker &> /dev/null; then
      apt-get update
      apt-get install -y ca-certificates curl gnupg
      install -m 0755 -d /etc/apt/keyrings
      curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
      echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
      apt-get update
      apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
      usermod -aG docker ${var.ssh_user}
    fi

    # Dossier de l'app
    mkdir -p /opt/toyboxing
    chown ${var.ssh_user}:${var.ssh_user} /opt/toyboxing
  EOT
}

# ── Bucket GCS : hébergement frontend statique ─────────
resource "google_storage_bucket" "frontend" {
  name          = "app-toyboxing-th-fchs-fr"
  location      = var.region
  force_destroy = true

  website {
    main_page_suffix = "index.html"
    not_found_page   = "index.html" # SPA fallback
  }

  uniform_bucket_level_access = true
}

# Accès public en lecture
resource "google_storage_bucket_iam_member" "frontend_public" {
  bucket = google_storage_bucket.frontend.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}
