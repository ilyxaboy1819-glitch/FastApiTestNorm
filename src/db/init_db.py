from src.db.session import engine
from src.db.base import Base

import src.models


def init_db():
    Base.metadata.create_all(bind=engine)