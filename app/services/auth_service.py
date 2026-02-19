# Créez ce nouveau fichier
def verify_admin_credentials(username, password):
    # Dans un vrai projet, vérifiez en BDD avec un hash de mot de passe
    if username == "admin" and password == "toyboxing2026":
        return "fake-jwt-token-for-admin"
    return None