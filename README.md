# ToyBoxing — Crazy Charly Day 2026

Projet complet (backend + frontend + infra) pour l'association **Toys Academy**. Des abonnes recoivent des box de jouets reconditionnes, composees sur mesure selon l'age de leur enfant et leurs preferences. Le backend gere le catalogue, les abonnes, et l'**optimisation automatique** de la composition des box.

```
Python 3.14 · Flask · SQLAlchemy + MySQL · React (Vite) · Docker · GCP · Cloudflare
```

**Production** : https://app-toyboxing.th-fchs.fr (front) — https://toyboxing.th-fchs.fr (API)

---

## Equipe

| Membre | Role |
|--------|------|
| **Thomas** | DevOps — deploiement complet (Terraform GCP, Docker, CI/CD, Cloudflare, bucket GCS) |
| **Geoffrey** | Backend Python / Flask, integration BDD MySQL (SQLAlchemy), debug |
| **Vivian** | Frontend React complet (interface admin + espace abonne) |
| **Marcelin** | Frontend React complet (interface admin + espace abonne) |

---

## Demarrage rapide

```bash
# Cloner et installer
git clone <repo-url> && cd BackWebApp
python3.14 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Lancer en dev (SQLite en memoire)
python run.py
# -> http://localhost:5000

# Lancer les tests
pytest

# Lancer avec Docker (MySQL)
cp .env.example .env   # editer les credentials
docker compose up -d

# Optimiseur en CLI (sans serveur)
python -m optimizer.cli tests/data/sample_input.csv
```

---

## Architecture

```
                    Cloudflare (DNS + HTTPS)
                         |
            +------------+------------+
            |                         |
   app-toyboxing.th-fchs.fr    toyboxing.th-fchs.fr
            |                         |
     GCS Bucket                 GCP VM (e2-small)
     [React build]                   |
                                   Nginx :80
                                     |
                                 Gunicorn :5000
                                 (Flask backend)
                                     |
                                  MySQL 8.0
```

### Structure du code

```
BackWebApp/
├── app/                          # Application Flask
│   ├── __init__.py               # Factory create_app() + SQLAlchemy
│   ├── config.py                 # Configs dev/test/prod (DB URI via env)
│   ├── models/                   # Modeles SQLAlchemy
│   │   ├── article.py            # Article + enums Category, AgeRange, Condition
│   │   ├── subscriber.py         # Subscriber (abonne)
│   │   ├── campaign.py           # Campaign + CampaignStatus
│   │   └── box.py                # Box + BoxHistoryEntry
│   ├── services/                 # Logique metier
│   ├── routes/                   # Blueprints Flask (endpoints REST)
│   └── utils/                    # Validators, pagination
│
├── optimizer/                    # Module independant (tourne aussi en CLI)
│   ├── scorer.py                 # 8 regles de scoring
│   ├── greedy.py                 # Algorithme glouton
│   ├── csv_io.py                 # Import/export CSV format sujet
│   ├── cli.py                    # CLI standalone
│   └── api.py                    # Pont Flask <-> optimizer
│
├── tests/                        # 45 tests pytest
├── terraform/                    # Infra GCP (VM + bucket)
├── .github/workflows/            # CI (lint+test) + CD (build+deploy)
├── docker-compose.yml            # nginx + backend + mysql
├── Dockerfile
└── nginx/nginx.conf
```

---

## Reference API

Toutes les reponses sont en JSON. Content-Type des requetes POST/PUT : `application/json`.

### Authentification admin

```
POST /admin/login
Body: { "username": "admin", "password": "..." }
-> { "token": "eyJ..." }
```

Le token JWT (8h) doit etre envoye dans le header `Authorization: Bearer <token>`.

### Enums

| Enum | Valeurs |
|------|---------|
| `category` | `SOC` `FIG` `CON` `EXT` `EVL` `LIV` |
| `age_range` | `BB` `PE` `EN` `AD` |
| `condition` | `N` `TB` `B` |
| `status` | `created` `optimized` `validated` |

### Endpoints

#### Admin — Articles
| Methode | Route | Description |
|---------|-------|-------------|
| POST | `/admin/articles` | Creer un article |
| GET | `/admin/articles?page=1&category=SOC&age_range=PE&condition=N` | Lister (pagine, filtres optionnels) |
| GET | `/admin/articles/{id}` | Detail |
| PUT | `/admin/articles/{id}` | Modifier (champs partiels) |

#### Admin — Abonnes
| Methode | Route | Description |
|---------|-------|-------------|
| GET | `/admin/subscribers` | Lister tous les abonnes |

#### Admin — Campagnes
| Methode | Route | Description |
|---------|-------|-------------|
| POST | `/admin/campaigns` | Creer (max_weight_per_box) |
| GET | `/admin/campaigns` | Lister |
| POST | `/admin/campaigns/{id}/optimize` | Lancer l'optimisation |
| GET | `/admin/campaigns/{id}/boxes` | Voir les box |
| POST | `/admin/campaigns/{id}/boxes/{sub_id}/validate` | Valider une box |

#### Admin — Dashboard et Historique
| Methode | Route | Description |
|---------|-------|-------------|
| GET | `/admin/dashboard` | Stats globales |
| GET | `/admin/history` | Historique des campagnes |

#### Espace abonne
| Methode | Route | Description |
|---------|-------|-------------|
| POST | `/subscriber/register` | Inscription |
| GET | `/subscriber/box?email=...` | Consulter sa box validee |
| PUT | `/subscriber/preferences` | Modifier preferences |
| GET | `/subscriber/history?email=...` | Historique personnel |

---

## Module d'optimisation

Le dossier `optimizer/` est independant de Flask. Il implemente les **8 regles de scoring** du sujet :

- **R1** Unicite (1 article = 1 box max)
- **R2** Compatibilite d'age
- **R3** Poids max par box
- **R4** Points par preference (10/8/6/4/2/1)
- **R5** Bonus etat (N=+2, TB=+1, B=+0)
- **R6** Utilites degressives (doublons de categorie)
- **R7** Malus -10 si 0 article
- **R8** Malus -10 par abonne avec 2+ articles de moins que le max

**Algorithme glouton** en 2 phases : assignation par max-heap puis equilibrage R8.

Score valide sur l'exemple du PDF : **70 points** (composition optimale).

---

## Tests

```bash
pytest                              # 45 tests
pytest --cov=app --cov=optimizer    # avec couverture
pytest tests/test_scorer.py -v      # un fichier specifique
```

| Fichier | Couverture |
|---------|-----------|
| `test_scorer.py` | 8 regles de scoring, exemples du PDF (62 et 70 pts) |
| `test_greedy.py` | Algorithme glouton, respect poids/age/unicite |
| `test_csv_io.py` | Parsing CSV, format sortie |
| `test_article_routes.py` | CRUD articles, pagination, filtres, suppression stock |
| `test_subscriber_routes.py` | Inscription, preferences, upsert |
| `test_campaign_routes.py` | Campagnes, optimisation, validation |
| `test_dashboard.py` | Dashboard, historique, box abonne |

---

## Deploiement

Le CI/CD est entierement automatise via GitHub Actions :

- **Push sur main (backend)** → lint ruff + tests → build Docker → push Docker Hub → deploy SSH sur la VM
- **Push sur main (frontend)** → build npm → upload GCS

Pour plus de details sur l'infrastructure, les problemes rencontres et les solutions : voir `docs/rapport-technique.md`.
