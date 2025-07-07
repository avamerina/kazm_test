from sqlalchemy import Column, String, Float, Date, DateTime, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base

# Association tables
genre_film_work = Table(
    'genre_film_work',
    Base.metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('genre_id', UUID(as_uuid=True), ForeignKey('content.genre.id'), nullable=False),
    Column('film_work_id', UUID(as_uuid=True), ForeignKey('content.film_work.id'), nullable=False),
    Column('created', DateTime, default=datetime.utcnow),
    schema='content'
)

person_film_work = Table(
    'person_film_work',
    Base.metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('person_id', UUID(as_uuid=True), ForeignKey('content.person.id'), nullable=False),
    Column('film_work_id', UUID(as_uuid=True), ForeignKey('content.film_work.id'), nullable=False),
    Column('role', Text, nullable=False),
    Column('created', DateTime, default=datetime.utcnow),
    schema='content'
)

class FilmWork(Base):
    __tablename__ = 'film_work'
    __table_args__ = {'schema': 'content'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    description = Column(Text)
    creation_date = Column(Date)
    rating = Column(Float)  # This corresponds to imdb_rating in the API
    type = Column(Text, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    genres = relationship("Genre", secondary=genre_film_work, back_populates="films", lazy="selectin")
    persons = relationship("Person", secondary=person_film_work, back_populates="films", lazy="selectin")

class Genre(Base):
    __tablename__ = 'genre'
    __table_args__ = {'schema': 'content'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text)
    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    films = relationship("FilmWork", secondary=genre_film_work, back_populates="genres", lazy="selectin")

class Person(Base):
    __tablename__ = 'person'
    __table_args__ = {'schema': 'content'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(Text, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    films = relationship("FilmWork", secondary=person_film_work, back_populates="persons", lazy="selectin") 