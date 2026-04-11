from sqlalchemy import Column, Integer, String, Text, Numeric, BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(14, 2), nullable=False)

    owner_phone = Column(String, nullable=False)
    extra_contact = Column(String, nullable=True)

    status = Column(String, default="pending_review", index=True)  # pending_review | published | rejected
    reject_reason = Column(Text, nullable=True)

    published_at = Column(DateTime, nullable=True)
    telegram_channel_message_id = Column(BigInteger, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    user = relationship("User")
    category = relationship("Category")
    region = relationship("Region")
    district = relationship("District")
    media_files = relationship("AdMedia", back_populates="ad")


class AdMedia(Base):
    __tablename__ = "ad_media"

    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(Integer, ForeignKey("ads.id"), nullable=False, index=True)
    media_type = Column(String, nullable=False)  # photo | video
    file_path = Column(String, nullable=False)
    file_id_telegram = Column(String, nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    ad = relationship("Ad", back_populates="media_files")
