from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from . import Base
from datetime import datetime

class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    room = Column(String, index=True)
    Temp = Column(Float)
    RelH = Column(Float)
    Occ = Column(Integer)
    Act = Column(Integer)
    Door = Column(Integer)
    Win = Column(Integer)
    L1 = Column(Integer) 
    L2 = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ComfortPreference(Base):
    __tablename__ = "comfort_preferences"

    id = Column(Integer, primary_key=True, index=True)
    room = Column(String, index=True)
    temperature = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RoomPreference(Base):
    __tablename__ = "room_preferences"

    id = Column(Integer, primary_key=True, index=True)
    room = Column(String, index=True, unique=True)
    temperature = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
