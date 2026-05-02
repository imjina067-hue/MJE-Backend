from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.domains.recommendation.service.dto.response.suggested_course_response_dto import (
    ActivitiesDto,
    CafesDto,
    CourseImageDto,
    ExplainTextDto,
    HashtagDto,
    LocationDto,
    OtherCourseItemDto,
    OtherCoursesDto,
    PlaceItemDto,
    RestaurantsDto,
)


class ExplainTextResponseForm(BaseModel):
    name: str
    description: str

    @classmethod
    def from_response(cls, dto: ExplainTextDto) -> ExplainTextResponseForm:
        return cls(name=dto.name, description=dto.description)


class KeywordItem(BaseModel):
    label: str


class HashtagResponseForm(BaseModel):
    keywords: list[KeywordItem]

    @classmethod
    def from_response(cls, dto: HashtagDto) -> HashtagResponseForm:
        return cls(keywords=[KeywordItem(label=kw) for kw in dto.keywords])


class LocationResponseForm(BaseModel):
    location: str

    @classmethod
    def from_response(cls, dto: LocationDto) -> LocationResponseForm:
        return cls(location=dto.location)


class ImageResponseForm(BaseModel):
    imageUrl: Optional[str]

    @classmethod
    def from_response(cls, dto: CourseImageDto) -> ImageResponseForm:
        return cls(imageUrl=dto.image_url)


class PlaceItem(BaseModel):
    id: str
    name: str
    description: str
    location: str
    time: Optional[str]
    imageUrl: Optional[str]

    @classmethod
    def from_dto(cls, dto: PlaceItemDto) -> PlaceItem:
        return cls(
            id=dto.id,
            name=dto.name,
            description=dto.description,
            location=dto.location,
            time=dto.time,
            imageUrl=dto.image_url,
        )


class RestaurantsResponseForm(BaseModel):
    restaurants: list[PlaceItem]

    @classmethod
    def from_response(cls, dto: RestaurantsDto) -> RestaurantsResponseForm:
        return cls(restaurants=[PlaceItem.from_dto(p) for p in dto.restaurants])


class CafesResponseForm(BaseModel):
    cafes: list[PlaceItem]

    @classmethod
    def from_response(cls, dto: CafesDto) -> CafesResponseForm:
        return cls(cafes=[PlaceItem.from_dto(p) for p in dto.cafes])


class ActivitiesResponseForm(BaseModel):
    activities: list[PlaceItem]

    @classmethod
    def from_response(cls, dto: ActivitiesDto) -> ActivitiesResponseForm:
        return cls(activities=[PlaceItem.from_dto(p) for p in dto.activities])


class OtherCourseItem(BaseModel):
    id: str
    name: str
    description: str
    locations: list[str]
    duration: Optional[int]
    imageUrl: Optional[str]

    @classmethod
    def from_dto(cls, dto: OtherCourseItemDto) -> OtherCourseItem:
        return cls(
            id=dto.id,
            name=dto.name,
            description=dto.description,
            locations=dto.locations,
            duration=dto.duration,
            imageUrl=dto.image_url,
        )


class OtherCoursesResponseForm(BaseModel):
    courses: list[OtherCourseItem]

    @classmethod
    def from_response(cls, dto: OtherCoursesDto) -> OtherCoursesResponseForm:
        return cls(courses=[OtherCourseItem.from_dto(c) for c in dto.courses])
