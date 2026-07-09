from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, Integer, ForeignKey

from app.core.db import Base, CatMixin


class Donation(CatMixin, Base):
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.id', name='fk_donation_user_id_user'),
        nullable=True
    )
