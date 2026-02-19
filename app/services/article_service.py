from __future__ import annotations

from app import db
from app.models.article import AgeRange, Article, Category, Condition

from app import db  # Importation de l'instance SQLAlchemy


def add_article(designation, category, age_range, condition, price, weight):
    # 1. Calculer le prochain ID (ex: a1, a2...)
    # On compte le nombre d'articles existants pour générer le suivant
    count = Article.query.count()
    new_id = f"a{count + 1}"

    # 2. Créer l'objet avec l'ID généré
    article = Article(
        id=new_id,
        designation=designation,
        category=category,
        age_range=age_range,
        condition=condition,
        price=price,
        weight=weight
    )

    db.session.add(article)
    db.session.commit()

    return article

def get_article(article_id: str) -> Article | None:
    return Article.query.get(article_id)


def list_articles(
        category: str | None = None,
        age_range: str | None = None,
        condition: str | None = None,
) -> list[Article]:
    result = list(Article.query.all())
    if category:
        result = [a for a in result if a.category.value == category]
    if age_range:
        result = [a for a in result if a.age_range.value == age_range]
    if condition:
        result = [a for a in result if a.condition.value == condition]
    return result


def update_article(
        article_id: str, **fields: object
) -> tuple[Article | None, str | None]:
    # 1. Recherche de l'article dans la base de données
    article = Article.query.get(article_id)
    if article is None:
        return None, "Article non trouvé"

    # 2. Vérification du verrouillage via la colonne 'is_locked' du modèle
    if article.is_locked:
        return None, "Article dans une box validée, modification interdite"

    # 3. Mise à jour dynamique des attributs
    for key, value in fields.items():
        if value is not None and hasattr(article, key):
            setattr(article, key, value)

    # 4. Sauvegarde des modifications (Commit)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return None, f"Erreur lors de la sauvegarde : {str(e)}"

    return article, None

def is_article_locked(article_id: str) -> bool:
    article = Article.query.get(article_id)
    # Retourne la valeur de la colonne 'is_locked' (True/False)
    return article.is_locked if article else False
