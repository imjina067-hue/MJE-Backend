from __future__ import annotations

from app.domains.recommendation.domain.exception import CourseNotFoundException
from app.domains.recommendation.service.dto.response.create_course_response_dto import (
    CourseResultDto,
    PlaceResultDto,
)
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
from app.domains.recommendation.service.port.course_store_port import CourseStorePort

_ACTIVITY_CATEGORIES = frozenset({"walk", "activity"})


class GetSuggestedCourseUseCase:

    def __init__(self, course_store: CourseStorePort) -> None:
        self._store = course_store

    def get_explain_text(self, course_id: str) -> ExplainTextDto:
        course = self._get_course(course_id)
        area = course.places[0].area if course.places else ""
        name = f"{area} {course.course_type}".strip() if area else course.course_type
        description = " -> ".join(p.name for p in course.places[:4])
        return ExplainTextDto(name=name, description=description)

    def get_hashtag(self, course_id: str) -> HashtagDto:
        course = self._get_course(course_id)
        seen: set[str] = set()
        keywords: list[str] = []
        for place in course.places:
            for kw in place.keywords:
                label = kw if kw.startswith("#") else f"#{kw}"
                if label not in seen:
                    seen.add(label)
                    keywords.append(label)
        return HashtagDto(keywords=keywords)

    def get_location(self, course_id: str) -> LocationDto:
        course = self._get_course(course_id)
        location = course.places[0].area if course.places else ""
        return LocationDto(location=location)

    def get_image(self, course_id: str) -> CourseImageDto:
        course = self._get_course(course_id)
        image_url = course.image_url or next(
            (p.image_url for p in course.places if p.image_url),
            None,
        )
        return CourseImageDto(image_url=image_url)

    def get_restaurants(self, course_id: str) -> RestaurantsDto:
        course = self._get_course(course_id)
        items = [
            self._to_place_item(p, course_id)
            for p in course.places
            if p.category == "restaurant"
        ]
        return RestaurantsDto(restaurants=items)

    def get_cafes(self, course_id: str) -> CafesDto:
        course = self._get_course(course_id)
        items = [
            self._to_place_item(p, course_id)
            for p in course.places
            if p.category == "cafe"
        ]
        return CafesDto(cafes=items)

    def get_activities(self, course_id: str) -> ActivitiesDto:
        course = self._get_course(course_id)
        items = [
            self._to_place_item(p, course_id)
            for p in course.places
            if p.category in _ACTIVITY_CATEGORIES
        ]
        return ActivitiesDto(activities=items)

    def get_other_courses(self, course_id: str) -> OtherCoursesDto:
        current_course = self._store.get_course(course_id)
        if current_course is None:
            raise CourseNotFoundException(course_id)

        courses = [
            self._to_other_course_item(course, idx)
            for idx, course in enumerate(self._store.get_other_courses(course_id))
        ]
        return OtherCoursesDto(courses=courses)

    def _get_course(self, course_id: str) -> CourseResultDto:
        course = self._store.get_course(course_id)
        if course is None:
            raise CourseNotFoundException(course_id)
        return course

    def _to_place_item(self, place: PlaceResultDto, course_id: str) -> PlaceItemDto:
        return PlaceItemDto(
            id=f"{course_id}_{place.visit_order}",
            name=place.name,
            description=place.main_description,
            location=place.area,
            time=place.recommended_time_slot,
            image_url=place.image_url,
        )

    def _to_other_course_item(
        self,
        course: CourseResultDto,
        idx: int,
    ) -> OtherCourseItemDto:
        locations = list(dict.fromkeys(p.area for p in course.places))
        image_url = course.image_url or next((p.image_url for p in course.places if p.image_url), None)
        description = " -> ".join(p.name for p in course.places[:3])
        return OtherCourseItemDto(
            id=course.course_id,
            course_id=course.course_id,
            name=course.course_type,
            description=description,
            locations=locations,
            duration=course.total_duration_minutes,
            image_url=image_url,
        )
