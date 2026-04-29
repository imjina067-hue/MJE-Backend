from dataclasses import dataclass


@dataclass(frozen=True)
class CreateCourseRequestDto:
    area: str
    start_time: str   # "HH:MM"
    transport: str    # "car" | "walk" | "public_transit"
