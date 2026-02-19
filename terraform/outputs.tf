output "vm_ip" {
  description = "IP publique de la VM — à ajouter dans Cloudflare (enregistrement A)"
  value       = google_compute_address.toyboxing.address
}

output "ssh_command" {
  description = "Commande SSH pour se connecter"
  value       = "ssh ${var.ssh_user}@${google_compute_address.toyboxing.address}"
}
