class InvalidEventNameException(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"허용되지 않는 이벤트명입니다: {name}")
