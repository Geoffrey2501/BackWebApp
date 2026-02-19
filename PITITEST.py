
import requests

BASE_URL = "http://localhost:10000"

def test_toyboxing_flow():
    print("--- Démarrage du test de l'API ToyBoxing ---\n")

    # 1. Créer un article
    print("[1] Création d'un article...")
    article_data = {
        "designation": "Monopoly Junior",
        "category": "SOC",
        "age_range": "PE",
        "condition": "N",
        "price": 8,
        "weight": 400
    }
    res = requests.post(f"{BASE_URL}/admin/articles", json=article_data)
    article = res.json()
    print(f"Article créé : {article['id']} - {article['designation']}")

    # 2. Inscrire un abonné
    print("\n[2] Inscription d'un abonné...")
    subscriber_data = {
        "first_name": "Alice",
        "last_name": "Dupont",
        "email": "alice@example.com",
        "child_age_range": "PE",
        "category_preferences": ["SOC", "FIG", "EVL", "CON", "LIV", "EXT"]
    }
    res = requests.post(f"{BASE_URL}/subscriber/register", json=subscriber_data)
    subscriber = res.json()
    print(f"Abonné inscrit : {subscriber['id']} ({subscriber['email']})")

    # 3. Créer une campagne
    print("\n[3] Création d'une campagne...")
    campaign_data = {"max_weight_per_box": 1200}
    res = requests.post(f"{BASE_URL}/admin/campaigns", json=campaign_data)
    campaign = res.json()
    campaign_id = campaign['id']
    print(f"Campagne créée : {campaign_id} (Poids max: 1200g)")

    # 4. Lancer l'optimisation
    print("\n[4] Lancement de l'optimisation...")
    res = requests.post(f"{BASE_URL}/admin/campaigns/{campaign_id}/optimize")
    if res.status_code == 200:
        boxes = res.json()
        print(f"Optimisation réussie : {len(boxes)} box(es) générée(s)")
    else:
        print(f"Erreur optimisation : {res.json()}")
        return

    # 5. Valider la box de l'abonné
    print(f"\n[5] Validation de la box pour l'abonné {subscriber['id']}...")
    url = f"{BASE_URL}/admin/campaigns/{campaign_id}/boxes/{subscriber['id']}/validate"
    res = requests.post(url)
    if res.status_code == 200:
        print("Box validée avec succès !")
    else:
        print(f"Erreur validation : {res.json()}")

    # 6. Vérifier la vue de l'abonné
    print("\n[6] Vérification de la box côté abonné...")
    res = requests.get(f"{BASE_URL}/subscriber/box?email={subscriber['email']}")
    if res.status_code == 200:
        box_details = res.json()
        print(f"Contenu de la box d'Alice : {[a['designation'] for a in box_details['articles']]}")
    else:
        print("La box n'est pas encore disponible pour l'abonné.")

    print("\n--- Tests terminés avec succès ---")

if __name__ == "__main__":
    try:
        test_toyboxing_flow()
    except Exception as e:
        print(f"\nErreur : Le serveur est-il bien lancé sur {BASE_URL} ?")
        print(f"Détail : {e}")
