from pydantic import BaseModel, UUID4, Field
from typing import List, Optional
from datetime import date, datetime

# Base schemas
class FilmBase(BaseModel):
    title: str
    description: Optional[str] = None
    creation_date: Optional[date] = None
    rating: Optional[float] = None
    type: str

class GenreBase(BaseModel):
    name: str
    description: Optional[str] = None

class PersonBase(BaseModel):
    full_name: str

# Create schemas
class FilmCreate(FilmBase):
    pass

class GenreCreate(GenreBase):
    pass

class PersonCreate(PersonBase):
    pass

# Update schemas
class FilmUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    creation_date: Optional[date] = None
    rating: Optional[float] = None
    type: Optional[str] = None

class GenreUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class PersonUpdate(BaseModel):
    full_name: Optional[str] = None

# Response schemas
class GenreResponse(GenreBase):
    uuid: UUID4 = Field(alias="id")

    class Config:
        from_attributes = True
        populate_by_name = True

class PersonResponse(PersonBase):
    uuid: UUID4 = Field(alias="id")

    class Config:
        from_attributes = True
        populate_by_name = True

class FilmResponse(FilmBase):
    uuid: UUID4 = Field(alias="id")

    class Config:
        from_attributes = True
        populate_by_name = True

# Detailed response schemas
class FilmDetailResponse(BaseModel):
    uuid: UUID4 = Field(alias="id")
    title: str
    imdb_rating: Optional[float] = None
    description: Optional[str] = None
    genre: List[GenreResponse] = []
    actors: List[PersonResponse] = []
    writers: List[PersonResponse] = []
    directors: List[PersonResponse] = []

    class Config:
        from_attributes = True
        populate_by_name = True

class PersonDetailResponse(BaseModel):
    uuid: UUID4 = Field(alias="id")
    full_name: str
    films: List[dict] = []

    class Config:
        from_attributes = True
        populate_by_name = True

class PersonFilmResponse(BaseModel):
    uuid: UUID4 = Field(alias="id")
    title: str
    imdb_rating: Optional[float] = None

    class Config:
        from_attributes = True
        populate_by_name = True

# Search response schemas
class FilmSearchResponse(BaseModel):
    uuid: UUID4 = Field(alias="id")
    title: str
    imdb_rating: Optional[float] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class PersonSearchResponse(BaseModel):
    uuid: UUID4 = Field(alias="id")
    full_name: str
    films: List[dict] = []

    class Config:
        from_attributes = True
        populate_by_name = True

# Pagination schemas
class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int

# AI Search schemas
class DescriptionSearchRequest(BaseModel):
    description: str
    limit: Optional[int] = 10

class FilmWithSimilarityResponse(BaseModel):
    uuid: UUID4 = Field(alias="id")
    title: str
    imdb_rating: Optional[float] = None
    similarity_score: float

    class Config:
        from_attributes = True
        populate_by_name = True

class DescriptionSearchResponse(BaseModel):
    films: List[FilmWithSimilarityResponse]
    total_results: int
    search_description: str
