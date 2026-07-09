from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text

from app.core.db import Base, CatMixin


MAX_NAME = 100


class CharityProject(CatMixin, Base):
    name: Mapped[str] = mapped_column(String(MAX_NAME), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
