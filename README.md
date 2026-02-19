# ToyBoxing — Backend API

Backend du projet **Crazy Charly Day 2026** pour l'association **Toys Academy**.

Le principe : des abonnés reçoivent des box de jouets reconditionnés, composées sur mesure selon l'âge de leur enfant et leurs préférences. Ce backend gère le catalogue d'articles, les abonnés, et surtout l'**optimisation automatique** de la composition des box.

```
Python 3.14 · Flask · Stockage en mémoire (pas de BDD) · pytest
```

---

## Sommaire

- [Démarrage rapide](#démarrage-rapide)
- [Architecture du projet](#architecture-du-projet)
- [Comment ça marche](#comment-ça-marche)
- [Référence API (pour le front)](#référence-api-pour-le-front)
- [Le module d'optimisation](#le-module-doptimisation)
- [Tests](#tests)

---

## Démarrage rapide

```bash
# Créer et activer le virtualenv
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install flask pytest pytest-cov ruff

# Lancer le serveur
python run.py
# → http://localhost:5000

# Lancer les tests
pytest

# Utiliser l'optimiseur en CLI (sans serveur)
python -m optimizer.cli tests/data/sample_input.csv
```

---

## Architecture du projet

```
BackWebApp/
│
├── app/                          ← Application Flask
│   ├── __init__.py               ← Factory  create_app()
│   ├── config.py                 ← Configs dev / test / prod
│   │
│   ├── models/                   ← Dataclasses (pas d'ORM)
│   │   ├── article.py            ← Article + enums Category, AgeRange, Condition
│   │   ├── subscriber.py         ← Subscriber (abonné)
│   │   ├── campaign.py           ← Campaign + CampaignStatus
│   │   └── box.py                ← Box + BoxHistoryEntry
│   │
│   ├── store/
│   │   └── memory_store.py       ← Singleton qui remplace la BDD
│   │
│   ├── services/                 ← Logique métier
│   │   ├── article_service.py
│   │   ├── subscriber_service.py
│   │   ├── campaign_service.py   ← Orchestration campagne + appel optimizer
│   │   ├── box_service.py
│   │   ├── dashboard_service.py
│   │   └── csv_service.py
│   │
│   ├── routes/                   ← Blueprints Flask (endpoints)
│   │   ├── admin_articles.py     ← /admin/articles
│   │   ├── admin_subscribers.py  ← /admin/subscribers
│   │   ├── admin_campaigns.py    ← /admin/campaigns
│   │   ├── admin_dashboard.py    ← /admin/dashboard
│   │   ├── admin_history.py      ← /admin/history
│   │   └── subscriber_routes.py  ← /subscriber
│   │
│   └── utils/
│       ├── validators.py         ← Validation email, enums, préférences
│       └── pagination.py         ← Pagination générique (10/page)
│
├── optimizer/                    ← Module indépendant de Flask
│   ├── models.py                 ← Dataclasses internes
│   ├── scorer.py                 ← Calcul de score (8 règles)
│   ├── greedy.py                 ← Algorithme glouton
│   ├── csv_io.py                 ← Lecture/écriture CSV format sujet
│   ├── cli.py                    ← Point d'entrée CLI standalone
│   └── api.py                    ← Pont Flask ↔ optimizer
│
├── tests/                        ← 45 tests pytest
├── run.py                        ← Point d'entrée dev
├── requirements.txt
└── pyproject.toml
```

Le projet est découpé en deux parties volontairement indépendantes : `app/` ne connaît `optimizer/` que via `optimizer/api.py`, et `optimizer/` peut tourner seul en CLI sans Flask.

---

## Comment ça marche

Le flux typique d'utilisation ressemble à ça :

```
                                ┌─────────────────────┐
                                │   1. Remplir le      │
                                │      catalogue       │
                                │   POST /admin/       │
                                │        articles      │
                                └─────────┬───────────┘
                                          │
                                          ▼
                  ┌───────────────────────────────────────────┐
                  │          2. Les abonnés s'inscrivent       │
                  │          POST /subscriber/register         │
                  │   (prénom, nom, email, âge enfant,         │
                  │    6 catégories classées par préférence)   │
                  └─────────────────────┬─────────────────────┘
                                        │
                                        ▼
                           ┌────────────────────────┐
                           │  3. Créer une campagne  │
                           │  POST /admin/campaigns  │
                           │  { max_weight: 1200 }   │
                           └────────────┬───────────┘
                                        │
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │        4. Lancer l'optimisation            │
                  │  POST /admin/campaigns/{id}/optimize       │
                  │                                           │
                  │  L'algorithme glouton compose les box :    │
                  │  - respecte la compatibilité d'âge         │
                  │  - maximise le score selon les préférences │
                  │  - respecte le poids max par box           │
                  │  - équilibre le nombre d'articles           │
                  └─────────────────────┬─────────────────────┘
                                        │
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │     5. Consulter & valider les box         │
                  │  GET  /admin/campaigns/{id}/boxes          │
                  │  POST .../boxes/{sub_id}/validate          │
                  │                                           │
                  │  La validation :                           │
                  │  - verrouille les articles (plus modif.)   │
                  │  - enregistre dans l'historique             │
                  │  - rend la box visible pour l'abonné       │
                  └─────────────────────┬─────────────────────┘
                                        │
                                        ▼
                           ┌────────────────────────┐
                           │  6. L'abonné consulte   │
                           │  GET /subscriber/box    │
                           │    ?email=alice@...     │
                           └────────────────────────┘
```

### Le stockage en mémoire

Pas de base de données. Tout vit dans un singleton `MemoryStore` : des dictionnaires Python, des listes, des compteurs auto-incrémentés. Les IDs sont générés séquentiellement : `a1, a2, a3...` pour les articles, `s1, s2...` pour les abonnés, `c1, c2...` pour les campagnes.

Quand un article se retrouve dans une box validée, il est "verrouillé" : une map inversée `validated_article_campaigns` empêche toute modification (l'API renvoie 409).

Tout est remis à zéro entre chaque test via `store.clear()`.

---

## Référence API (pour le front)

Toutes les réponses sont en JSON. Le Content-Type des requêtes POST/PUT doit être `application/json`.

### Modèles de données

Avant de lire les routes, voici les structures que l'API manipule :

**Article**
```json
{
  "id": "a1",
  "designation": "Monopoly Junior",
  "category": "SOC",
  "age_range": "PE",
  "condition": "N",
  "price": 8,
  "weight": 400
}
```

**Subscriber**
```json
{
  "id": "s1",
  "first_name": "Alice",
  "last_name": "Dupont",
  "email": "alice@example.com",
  "child_age_range": "PE",
  "category_preferences": ["SOC", "FIG", "EVL", "CON", "LIV", "EXT"]
}
```

**Campaign**
```json
{
  "id": "c1",
  "max_weight_per_box": 1200,
  "status": "created"
}
```

**Box** (après optimisation)
```json
{
  "campaign_id": "c1",
  "subscriber_id": "s1",
  "article_ids": ["a1", "a2", "a4"],
  "validated": false,
  "score": 27,
  "total_weight": 1000,
  "total_price": 17
}
```

### Valeurs possibles des enums

| Enum | Valeurs | Signification |
|------|---------|---------------|
| `category` | `SOC` `FIG` `CON` `EXT` `EVL` `LIV` | Jeux de société, Figurines, Construction, Extérieur, Éveil, Livres |
| `age_range` | `BB` `PE` `EN` `AD` | 0-3 ans, 3-6 ans, 6-10 ans, 10+ ans |
| `condition` | `N` `TB` `B` | Neuf, Très bon état, Bon état |
| `status` (campagne) | `created` `optimized` `validated` | Créée, Optimisée, Validée |

---

### Admin — Articles

Le CRUD principal du catalogue. La liste est paginée par 10 et filtrable.

```
POST   /admin/articles
GET    /admin/articles?page=1&category=SOC&age_range=PE&condition=N
GET    /admin/articles/{id}
PUT    /admin/articles/{id}
```

#### Créer un article

```
POST /admin/articles
```

**Body :**
```json
{
  "designation": "Monopoly Junior",
  "category": "SOC",
  "age_range": "PE",
  "condition": "N",
  "price": 8,
  "weight": 400
}
```

Tous les champs sont obligatoires. `price` est un entier >= 0, `weight` un entier > 0.

| Réponse | Description |
|---------|-------------|
| `201` | Article créé, retourne l'objet avec l'`id` auto-généré |
| `400` | `{ "errors": ["designation requis", "category invalide", ...] }` |

#### Lister les articles (paginé + filtres)

```
GET /admin/articles?page=1&category=SOC&age_range=PE&condition=N
```

Tous les query params sont optionnels. Les filtres se combinent (ET logique).

**Réponse 200 :**
```json
{
  "items": [ /* ... articles ... */ ],
  "page": 1,
  "total_pages": 3,
  "total": 25
}
```

#### Détail d'un article

```
GET /admin/articles/a1
```

| Réponse | Description |
|---------|-------------|
| `200` | L'objet Article |
| `404` | `{ "error": "Article non trouvé" }` |

#### Modifier un article

```
PUT /admin/articles/a1
```

**Body :** n'importe quel sous-ensemble des champs. Seuls les champs fournis sont modifiés.
```json
{
  "designation": "Monopoly Junior Edition 2026",
  "price": 10
}
```

| Réponse | Description |
|---------|-------------|
| `200` | Article modifié |
| `400` | Valeur invalide |
| `404` | Article non trouvé |
| `409` | Article verrouillé (dans une box validée) |

---

### Admin — Abonnés

```
GET /admin/subscribers
```

Retourne la liste complète de tous les abonnés (pas de pagination).

**Réponse 200 :** `[ Subscriber, ... ]`

---

### Admin — Campagnes

C'est ici que tout se joue : création, optimisation, consultation et validation des box.

```
POST   /admin/campaigns
GET    /admin/campaigns
POST   /admin/campaigns/{id}/optimize
GET    /admin/campaigns/{id}/boxes
POST   /admin/campaigns/{id}/boxes/{subscriber_id}/validate
```

#### Créer une campagne

```
POST /admin/campaigns
```

**Body :**
```json
{
  "max_weight_per_box": 1200
}
```

| Réponse | Description |
|---------|-------------|
| `201` | Campagne créée avec `status: "created"` |
| `400` | Poids invalide |

#### Lister les campagnes

```
GET /admin/campaigns
```

**Réponse 200 :** `[ Campaign, ... ]`

#### Lancer l'optimisation

```
POST /admin/campaigns/c1/optimize
```

Pas de body. L'optimiseur tourne sur tous les articles et abonnés actuellement en mémoire. Le status passe à `"optimized"`.

| Réponse | Description |
|---------|-------------|
| `200` | Liste des box composées `[ Box, ... ]` |
| `400` | Campagne non trouvée, déjà optimisée, ou aucun abonné |

#### Voir les box d'une campagne

```
GET /admin/campaigns/c1/boxes
```

Chaque box est enrichie avec le détail des articles et le nom de l'abonné :

**Réponse 200 :**
```json
[
  {
    "campaign_id": "c1",
    "subscriber_id": "s1",
    "article_ids": ["a1", "a2", "a4"],
    "validated": false,
    "score": 27,
    "total_weight": 1000,
    "total_price": 17,
    "subscriber_name": "Alice Dupont",
    "articles": [
      { "id": "a1", "designation": "Monopoly Junior", "category": "SOC", ... },
      { "id": "a2", "designation": "Barbie Aventurière", "category": "FIG", ... },
      { "id": "a4", "designation": "Cubes alphabet", "category": "CON", ... }
    ]
  }
]
```

#### Valider une box

```
POST /admin/campaigns/c1/boxes/s1/validate
```

Effets de la validation :
- La box passe à `validated: true`
- Les articles de la box sont verrouillés (plus modifiables)
- Un snapshot est ajouté dans l'historique
- L'abonné peut désormais voir sa box via `/subscriber/box`

| Réponse | Description |
|---------|-------------|
| `200` | Box validée |
| `400` | Box non trouvée ou déjà validée |

---

### Admin — Dashboard

```
GET /admin/dashboard
```

**Réponse 200 :**
```json
{
  "articles_by_category": { "SOC": 5, "FIG": 3, "CON": 8, ... },
  "articles_by_age_range": { "BB": 2, "PE": 10, "EN": 6, "AD": 4 },
  "articles_by_condition": { "N": 8, "TB": 7, "B": 7 },
  "total_articles": 22,
  "active_subscribers": 12,
  "subscribers_by_age_range": { "PE": 5, "EN": 4, "BB": 2, "AD": 1 },
  "average_box_score": 24.5,
  "total_validated_boxes": 8
}
```

---

### Admin — Historique

```
GET /admin/history
```

Retourne l'historique de toutes les campagnes dont au moins une box a été validée, avec des statistiques agrégées.

**Réponse 200 :**
```json
[
  {
    "campaign_id": "c1",
    "nb_boxes": 3,
    "total_articles": 8,
    "total_score": 70,
    "average_score": 23.33,
    "boxes": [
      {
        "campaign_id": "c1",
        "subscriber_id": "s1",
        "article_ids": ["a1", "a2", "a4"],
        "score": 27,
        "total_weight": 1000,
        "total_price": 17,
        "timestamp": "2026-02-19T14:30:00.000000"
      }
    ]
  }
]
```

---

### Espace abonné

Routes pour l'interface abonné. Pas d'authentification : l'abonné s'identifie par email. Un cookie `subscriber_email` est posé à l'inscription.

```
POST   /subscriber/register
GET    /subscriber/box?email=...
PUT    /subscriber/preferences
GET    /subscriber/history?email=...
```

#### S'inscrire

```
POST /subscriber/register
```

**Body :**
```json
{
  "first_name": "Alice",
  "last_name": "Dupont",
  "email": "alice@example.com",
  "child_age_range": "PE",
  "category_preferences": ["SOC", "FIG", "EVL", "CON", "LIV", "EXT"]
}
```

Les préférences sont les 6 catégories classées de la plus souhaitée à la moins souhaitée. Toutes les 6 doivent être présentes, sans doublon.

Si l'email existe déjà, les informations de l'abonné sont mises à jour (pas de doublon).

| Réponse | Description |
|---------|-------------|
| `201` | Abonné créé/mis à jour + cookie `subscriber_email` posé |
| `400` | `{ "errors": [...] }` |

#### Consulter sa box

```
GET /subscriber/box?email=alice@example.com
```

Ne retourne que les box **validées**. La réponse inclut le détail complet des articles.

| Réponse | Description |
|---------|-------------|
| `200` | Box enrichie (articles + subscriber_name) |
| `404` | Abonné non trouvé ou aucune box validée |

#### Modifier ses préférences

```
PUT /subscriber/preferences
```

**Body :**
```json
{
  "email": "alice@example.com",
  "child_age_range": "EN",
  "category_preferences": ["EXT", "CON", "SOC", "EVL", "FIG", "LIV"]
}
```

`child_age_range` et `category_preferences` sont optionnels (seuls les champs fournis sont modifiés). `email` est obligatoire pour identifier l'abonné.

| Réponse | Description |
|---------|-------------|
| `200` | Abonné mis à jour |
| `400` | Valeurs invalides |
| `404` | Abonné non trouvé |

#### Historique personnel

```
GET /subscriber/history?email=alice@example.com
```

Retourne toutes les box validées passées de l'abonné, avec le détail des articles.

**Réponse 200 :** `[ { BoxHistoryEntry + "articles": [...] }, ... ]`

---

## Le module d'optimisation

Le dossier `optimizer/` est un module Python indépendant. Il n'importe rien de Flask et peut tourner seul.

### Les 8 règles de scoring

Le score mesure la qualité d'une composition. L'objectif de l'algorithme est de le **maximiser**.

```
Score total = somme des points par article + bonus d'état - malus box vide - malus inéquité
              \___________ R4 ___________/  \__ R5 __/   \____ R7 ____/   \____ R8 ____/
                     avec R6 (dégressivité)
```

**R1 — Unicité :** chaque article dans une seule box max.

**R2 — Compatibilité d'âge :** un article ne va que dans la box d'un abonné dont l'enfant est de la même tranche d'âge.

**R3 — Poids max :** le poids total d'une box ne dépasse pas la limite de la campagne.

**R4 — Points par préférence :** un article rapporte des points selon la position de sa catégorie dans les préférences de l'abonné :

```
Rang de préférence :   1er    2e    3e    4e    5e    6e
Points :                10     8     6     4     2     1
```

**R5 — Bonus d'état :** chaque article ajoute un bonus selon son état :

```
N (Neuf) → +2    TB (Très bon) → +1    B (Bon) → +0
```

**R6 — Utilités dégressives :** si un abonné a plusieurs articles de la même catégorie, chaque doublon est scoré comme si la catégorie était un rang plus bas. Exemple : si SOC est en 1er choix et qu'on met 2 articles SOC, le 1er vaut 10 pts, le 2e vaut 8 pts (rang décalé de 1).

**R7 — Malus box vide :** si un abonné ne reçoit aucun article → **-10 points**.

**R8 — Malus inéquité :** si un abonné a 2 articles de moins (ou plus) que celui qui en a le plus → **-10 points** par abonné concerné.

### Exemple concret (du sujet)

Avec 8 articles, 3 abonnés (Alice PE, Bob EN, Clara PE), poids max 1200g :

```
Composition naïve (score 62) :         Composition optimale (score 70) :

Alice : a1(SOC) a2(FIG) a3(EVL)        Alice : a1(SOC) a2(FIG) a4(CON)
  → 12 + 9 + 7 = 28 pts                 → 12 + 9 + 6 = 27 pts

Bob   : a7(EXT) a6(CON)                Bob   : a7(EXT) a6(CON) a8(LIV)
  → 12 + 8 = 20 pts                     → 12 + 8 + 2 = 22 pts

Clara : a4(CON) a5(LIV)                Clara : a3(EVL) a5(LIV)
  → 4 + 10 = 14 pts                     → 11 + 10 = 21 pts

Total : 62                              Total : 70
```

En cédant a3 (EVL, 1er choix de Clara) et en redistribuant, tout le monde y gagne.

### L'algorithme glouton

L'optimiseur fonctionne en deux phases :

```
Phase 1 — Assignation gloutonne par max-heap
──────────────────────────────────────────────
  Pour chaque paire (abonné, article) compatible en âge :
    → calculer le gain marginal (points préf. + bonus état)
    → pousser dans un tas max (priority queue)

  Tant que le tas n'est pas vide :
    → extraire la paire avec le meilleur gain
    → si l'article est déjà pris → ignorer
    → si le poids dépasse la limite → ignorer
    → si le gain a changé (à cause de R6) → re-pousser avec le bon gain
    → sinon → assigner l'article à l'abonné

Phase 2 — Équilibrage (R8)
──────────────────────────
  Tant que l'écart max d'articles entre abonnés >= 2 :
    → pour chaque abonné déficitaire :
      → trouver le meilleur article non assigné compatible
      → l'ajouter si le poids le permet
```

### Utilisation en CLI

```bash
# Sortie sur stdout
python -m optimizer.cli tests/data/sample_input.csv

# Sortie dans un fichier
python -m optimizer.cli tests/data/sample_input.csv -o resultat.csv
```

Le format d'entrée CSV utilise le séparateur `;` avec trois sections :

```
articles
a1;Monopoly Junior;SOC;PE;N;8;400
a2;Barbie Aventurière;FIG;PE;TB;5;300
...

abonnes
s1;Alice;PE;SOC,FIG,EVL,CON,LIV,EXT
s2;Bob;EN;EXT,CON,SOC,EVL,FIG,LIV
...

parametres
1200
```

Le format de sortie :

```
70
Alice;a1;SOC;PE;N
Alice;a2;FIG;PE;TB
Alice;a4;CON;PE;N
Bob;a7;EXT;EN;N
Bob;a6;CON;EN;B
Bob;a8;LIV;EN;TB
Clara;a3;EVL;PE;TB
Clara;a5;LIV;PE;N
```

Première ligne = score total, puis une ligne par article affecté.

---

## Tests

45 tests couvrent l'ensemble du projet :

```bash
# Tous les tests
pytest

# Avec couverture
pytest --cov=app --cov=optimizer

# Un fichier en particulier
pytest tests/test_scorer.py -v
```

| Fichier de test | Ce qu'il couvre |
|-----------------|-----------------|
| `test_scorer.py` | Les 8 règles de scoring, validation contre les exemples du PDF (62 et 70 points) |
| `test_greedy.py` | Algorithme glouton : score >= 62, respect du poids, compatibilité âge, unicité |
| `test_csv_io.py` | Parsing CSV (y compris `;` parasites), format de sortie |
| `test_article_routes.py` | CRUD articles, pagination, filtres, verrouillage 409 |
| `test_subscriber_routes.py` | Inscription, mise à jour, upsert par email, préférences |
| `test_campaign_routes.py` | Création, optimisation, consultation des box, validation |
| `test_dashboard.py` | Dashboard stats, historique, consultation box abonné |

Le `conftest.py` fournit les fixtures `client` (test client Flask), `sample_articles` (8 articles du PDF) et `sample_subscribers` (Alice, Bob, Clara). Le store est réinitialisé automatiquement entre chaque test.
