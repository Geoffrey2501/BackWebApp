import pytest

from app import create_app
from app.models.article import AgeRange, Category, Condition
from app.services import article_service, subscriber_service

@pytest.fixture()
def app():
    application = create_app("test")
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def reset_store():
    store.clear()
    yield
    store.clear()


@pytest.fixture()
def sample_articles():
    """Load the 8 articles from the PDF example."""
    data = [
        ("Monopoly Junior", Category.SOC, AgeRange.PE, Condition.N, 8, 400),
        ("Barbie Aventurière", Category.FIG, AgeRange.PE, Condition.TB, 5, 300),
        ("Puzzle éducatif", Category.EVL, AgeRange.PE, Condition.TB, 7, 350),
        ("Cubes alphabet", Category.CON, AgeRange.PE, Condition.N, 4, 300),
        ("Livre cache-cache", Category.LIV, AgeRange.PE, Condition.N, 3, 200),
        ("Kapla 200 pièces", Category.CON, AgeRange.EN, Condition.B, 10, 600),
        ("Cerf-volant Pirate", Category.EXT, AgeRange.EN, Condition.N, 6, 400),
        ("Le Petit Nicolas", Category.LIV, AgeRange.EN, Condition.TB, 5, 200),
    ]
    articles = []
    for designation, cat, age, cond, price, weight in data:
        art = article_service.add_article(designation, cat, age, cond, price, weight)
        articles.append(art)
    return articles


@pytest.fixture()
def sample_subscribers():
    """Load the 3 subscribers from the PDF example."""
    subs = []
    subs.append(subscriber_service.register_subscriber(
        "Alice", "Dupont", "alice@test.com",
        AgeRange.PE,
        [Category.SOC, Category.FIG, Category.EVL, Category.CON, Category.LIV, Category.EXT],
    ))
    subs.append(subscriber_service.register_subscriber(
        "Bob", "Martin", "bob@test.com",
        AgeRange.EN,
        [Category.EXT, Category.CON, Category.SOC, Category.EVL, Category.FIG, Category.LIV],
    ))
    subs.append(subscriber_service.register_subscriber(
        "Clara", "Bernard", "clara@test.com",
        AgeRange.PE,
        [Category.EVL, Category.LIV, Category.FIG, Category.SOC, Category.CON, Category.EXT],
    ))
    return subs
