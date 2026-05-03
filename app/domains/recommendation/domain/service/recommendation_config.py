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
    "activity": {
        "morning": [
            "공원 산책",
            "미술관 전시 갤러리",
            "서점 문화공간",
        ],
        "lunch": [
            "미술관 전시 갤러리 영화",
            "볼링 방탈출 클라이밍 보드게임카페",
            "편집숍 소품샵 빈티지 복합쇼핑몰",
            "공원 산책 서점",
        ],
        "afternoon": [
            "미술관 전시 갤러리 영화",
            "볼링 방탈출 클라이밍 보드게임카페",
            "공방 원데이클래스 도자기 향수만들기",
            "편집숍 소품샵 빈티지 복합쇼핑몰 전통시장",
            "공원 산책 루프탑 자전거대여",
            "서점 문화공간 전시",
        ],
        "evening": [
            "미술관 전시 영화",
            "볼링 방탈출 클라이밍",
            "공원 루프탑",
            "칵테일바 와인바 루프탑바 LP바",
            "홀덤펍 이색주점",
            "공원 산책 야경 영화",
        ],
        "late_night": [
            "칵테일바 와인바 루프탑바 LP바",
            "홀덤펍 이색주점",
            "자동차극장 심야영화",
            "심야영화",
        ],
    },
}

# Keep the 3-axis structure, but let activity recover with walk/culture style queries
# when the primary activity search is too sparse for a given area/time slot.
ACTIVITY_FALLBACK_SEARCH_KEYWORDS: dict[str, list[str]] = {
    "morning": [
        "공원 산책",
        "전시 갤러리",
        "서점 문화공간",
    ],
    "lunch": [
        "공원 산책",
        "전시 갤러리 영화",
        "편집숍 소품샵",
    ],
    "afternoon": [
        "공원 산책 루프탑",
        "전시 갤러리 영화",
        "편집숍 소품샵 빈티지",
    ],
    "evening": [
        "전시 영화 루프탑",
        "공원 산책 야경",
        "칵테일바 와인바",
    ],
    "late_night": [
        "칵테일바 와인바 LP바",
        "심야영화 자동차극장",
        "이색주점 홀덤펍",
    ],
}
