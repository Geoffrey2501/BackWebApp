def verify_admin_credentials(username, password):
    if username == "admin" and password == "toyboxing2026":
        return "fake-jwt-token-for-admin"
    return None