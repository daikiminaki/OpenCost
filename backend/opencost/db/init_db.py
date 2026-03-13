from sqlalchemy import select

from opencost.db.base import Base
from opencost.db.session import SessionLocal, engine
from opencost.models.models import ModelPriceSnapshot
from opencost.pricing.engine import load_price_seed


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    seed = load_price_seed()
    with SessionLocal() as db:
        for item in seed:
            exists = db.scalar(
                select(ModelPriceSnapshot).where(
                    ModelPriceSnapshot.provider == item["provider"],
                    ModelPriceSnapshot.model == item["model"],
                )
            )
            if not exists:
                db.add(ModelPriceSnapshot(**item))
        db.commit()
