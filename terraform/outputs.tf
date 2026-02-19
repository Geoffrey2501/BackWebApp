output "vm_ip" {
  description = "IP publique de la VM — à ajouter dans Cloudflare (enregistrement A)"
  value       = google_compute_address.toyboxing.address
}

output "ssh_command" {
  description = "Commande SSH pour se connecter"
  value       = "ssh ${var.ssh_user}@${google_compute_address.toyboxing.address}"
}

output "frontend_bucket_url" {
  description = "URL du bucket frontend (à mettre en CNAME dans Cloudflare)"
  value       = "c.storage.googleapis.com"
}

output "frontend_bucket_name" {
  description = "Nom du bucket pour le déploiement"
  value       = google_storage_bucket.frontend.name
}
