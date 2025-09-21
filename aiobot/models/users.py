from datetime import datetime

from sqlalchemy import Column, Integer, String, update, delete, Date
from sqlalchemy.future import select

from aiobot.database import Base, db


# auto create id
class Users(Base):
    __tablename__ = "users"
    user_id = Column(String(50), unique=True)
    full_name = Column(String(30))
    phone_number = Column(String(30))
    lang = Column(String(2))
    status = Column(String, default='user')
    created_at = Column(Date, default=datetime.now())

    def __repr__(self):
        return f'<{self.__class__.__name__:} pk={self.pk}, user_id={self.user_id}, full_name={self.full_name}, score={self.score}, status={self.status}>'

    @classmethod
    async def create(cls, user_id, **kwargs):
        user = cls(user_id=user_id, **kwargs)  # noqa
        db.add(user)
        await cls.commit()
        return user

    @classmethod
    async def get(cls, user_id):
        query = select(cls).where(cls.user_id == user_id)
        result = await db.execute(query)
        user = result.scalars().first()
        return user

    @classmethod
    async def get_all(cls):
        query = select(cls)
        users = await db.execute(query)
        return users

    @classmethod
    async def update(cls, user_id, **kwargs):
        query = (
            update(cls)
            .where(cls.user_id == user_id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(query)
        await cls.commit()

    @classmethod
    async def delete(cls, user_id):
        query = delete(cls).where(cls.user_id == user_id)
        await db.execute(query)
        await cls.commit()
        return True

    @classmethod
    async def get_language(cls, user_id):
        user = await cls.get(user_id)
        if user and hasattr(user, "lang"):
            return user.lang
        return "ru"