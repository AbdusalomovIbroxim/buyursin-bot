from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, update, delete, BigInteger, Float
from sqlalchemy.future import select

from aiobot.database import Base, db

class Ads(Base):
    __tablename__ = "ads"
    user_id = Column(BigInteger, ForeignKey('users.pk'))
    title = Column(String)
    price = Column(Float)
    size = Column(String)
    condition = Column(String)
    defect_info = Column(String, nullable=True)
    photos = Column(String)
    status = Column(String, default='pending')
    admin_message_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    @classmethod
    async def create(cls, user_id, title, price, size, condition, photos, status='pending'):
        ad = cls(
            user_id=user_id,
            title=title,
            price=price,
            size=size,
            condition=condition,
            photos=photos,
            status=status
        )
        db.add(ad)
        await cls.commit()
        return ad

    @classmethod
    async def get(cls, ad_id):
        query = select(cls).where(cls.pk == ad_id)
        result = await db.execute(query)
        ad = result.scalar_one_or_none()
        return ad

    @classmethod
    async def update_status(cls, ad_id, status):
        query = (
            update(cls)
            .where(cls.pk == ad_id)
            .values(status=status)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(query)
        await cls.commit()

    @classmethod
    async def update_admin_message_id(cls, ad_id, message_id):
        query = (
            update(cls)
            .where(cls.pk == ad_id)
            .values(admin_message_id=message_id)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(query)
        await cls.commit()

    @classmethod
    async def delete(cls, ad_id):
        query = delete(cls).where(cls.pk == ad_id)
        await db.execute(query)
        await cls.commit()
        return True 