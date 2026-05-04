from __future__ import annotations

TOP_N_CANDIDATES: int = 20
MIN_ACTIVITY_CANDIDATES: int = 6

SCORE_WEIGHTS: dict[str, float] = {
    "search_rank": 0.40,
    "rating": 0.35,
    "trend": 0.15,
    "time_fit": 0.10,
}

PARKING_BONUS: float = 0.10
FRANCHISE_SCORE_MULTIPLIER: float = 0.3

NIGHTLIFE_SIGNALS: frozenset[str] = frozenset({
    "주점",
    "술집",
    "포차",
    "이자카야",
    "바",
    "펍",
    "칵테일바",
    "루프탑바",
    "심야식당",
})

COURSE_PATTERNS: list[list[str]] = [
    ["restaurant", "cafe", "activity"],
    ["cafe", "restaurant", "activity"],
    ["activity", "restaurant", "cafe"],
    ["restaurant", "activity", "cafe"],
    ["cafe", "activity", "restaurant"],
    ["activity", "cafe", "restaurant"],
]

FALLBACK_COURSE_PATTERNS: list[list[str]] = [
    ["restaurant", "cafe"],
    ["cafe", "activity"],
    ["restaurant", "activity"],
    ["activity", "cafe"],
    ["cafe", "restaurant"],
    ["activity", "restaurant"],
]

# Time-slot aware search keywords. The direction stays the same,
# but each slot keeps at least one broader query so candidates do not dry up too easily.
CATEGORY_SEARCH_KEYWORDS: dict[str, dict[str, list[str]]] = {
    "restaurant": {
        "morning": ["브런치 카페 조식", "브런치 맛집"],
        "lunch": ["맛집 음식점 레스토랑", "점심 맛집"],
        "afternoon": ["맛집 음식점 레스토랑", "식사 맛집"],
        "evening": ["맛집 음식점 이자카야 레스토랑", "맛집 음식점"],
        "late_night": ["심야식당 이자카야 술집 포차", "맛집 이자카야"],
    },
    "cafe": {
        "morning": ["카페 커피 브런치", "브런치 카페"],
        "lunch": ["카페 커피 디저트", "디저트 카페"],
        "afternoon": ["카페 커피 디저트", "테마 카페"],
        "evening": ["카페 와인바 칵테일바", "카페 커피 디저트"],
        "late_night": ["칵테일바 와인바 루프탑바 LP바", "카페 와인바"],
    },
}

ACTIVITY_SUBTYPE_SEARCH_KEYWORDS: dict[str, dict[str, list[str]]] = {
    "morning": {
        "walk": ["산책", "공원", "한강공원"],
        "culture": ["전시", "갤러리", "서점"],
    },
    "lunch": {
        "culture": ["전시", "갤러리", "영화관"],
        "experience": ["공방", "원데이클래스", "체험"],
        "walk": ["산책", "공원", "루프탑"],
        "shopping": ["편집숍", "소품샵", "빈티지샵"],
    },
    "afternoon": {
        "culture": ["전시", "갤러리", "미술관"],
        "experience": ["공방", "원데이클래스", "향수공방"],
        "walk": ["산책", "공원", "루프탑"],
        "shopping": ["편집숍", "소품샵", "쇼룸"],
    },
    "evening": {
        "culture": ["전시", "영화관"],
        "experience": ["방탈출", "볼링장", "보드게임카페"],
        "walk": ["산책", "야경", "루프탑"],
        "nightlife": ["와인바", "칵테일바", "lp바"],
        "shopping": ["편집숍", "쇼룸"],
    },
    "late_night": {
        "walk": ["야경", "산책"],
        "nightlife": ["와인바", "칵테일바", "lp바"],
        "culture": ["심야영화", "자동차극장"],
    },
}

ACTIVITY_SUBTYPE_FALLBACK_SEARCH_KEYWORDS: dict[str, dict[str, list[str]]] = {
    "morning": {
        "walk": ["산책"],
        "culture": ["전시"],
    },
    "lunch": {
        "walk": ["산책"],
        "culture": ["전시"],
        "shopping": ["소품샵"],
    },
    "afternoon": {
        "walk": ["산책"],
        "culture": ["갤러리"],
        "experience": ["공방"],
    },
    "evening": {
        "walk": ["야경"],
        "nightlife": ["와인바"],
        "culture": ["전시"],
    },
    "late_night": {
        "walk": ["야경"],
        "nightlife": ["칵테일바"],
        "culture": ["심야영화"],
    },
}

ACTIVITY_SUBTYPE_SIGNALS: dict[str, tuple[str, ...]] = {
    "culture": ("전시", "갤러리", "미술관", "박물관", "영화관", "서점"),
    "experience": ("공방", "원데이", "클래스", "체험", "향수", "도자기", "방탈출", "볼링", "보드게임"),
    "walk": ("산책", "공원", "야경", "루프탑", "한강"),
    "nightlife": ("와인바", "칵테일바", "lp바", "펍", "바", "주점"),
    "shopping": ("편집숍", "소품샵", "빈티지", "쇼룸", "복합문화공간"),
}
