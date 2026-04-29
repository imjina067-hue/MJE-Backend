# Project Overview

Pioneer Team Backend — a Python FastAPI application.

---

# Commands

- Run dev server: `uvicorn main:app --reload --host 0.0.0.0 --port 33333`
- Run directly: `python main.py`

---

# 목적

이 프로젝트는 FastAPI 기반 Layered Architecture + Domain Driven Design (DDD) 구조를 따른다.

## 목표

- 계층 간 책임 분리를 명확히 한다
- 비즈니스 로직의 위치를 강제한다
- 데이터 흐름을 일관되게 유지한다
- 유지보수성과 확장성을 확보한다

> 이 문서의 규칙은 MUST 준수되어야 한다.

---

# 다음과 같은 프로젝트 구조를 따른다

app
 ├ domains
 │   ├ recommendation
 │   │   ├ domain
 │   │   │   ├ entity
 │   │   │   ├ value_object
 │   │   │   └ service
 │   │   │
 │   │   ├ service
 │   │   │   ├ usecase
 │   │   │   └ dto
 │   │   │       ├ request
 │   │   │       └ response
 │   │   │
 │   │   ├ controller
 │   │   │   └ api
 │   │   │       ├ request_form
 │   │   │       └ response_form
 │   │   │
 │   │   └ repository
 │   │       ├ orm
 │   │       └ mapper
 │   │
 │   ├ export
 │   │   ├ domain
 │   │   │   ├ entity
 │   │   │   ├ value_object
 │   │   │   └ service
 │   │   │
 │   │   ├ service
 │   │   │   ├ usecase
 │   │   │   └ dto
 │   │   │       ├ request
 │   │   │       └ response
 │   │   │
 │   │   ├ controller
 │   │   │   └ api
 │   │   │       ├ request_form
 │   │   │       └ response_form
 │   │   │
 │   │   └ repository
 │   │       ├ orm
 │   │       └ mapper
 │   │
 │   └ tracking
 │       ├ domain
 │       │   ├ entity
 │       │   ├ value_object
 │       │   └ service
 │       │
 │       ├ service
 │       │   ├ usecase
 │       │   └ dto
 │       │       ├ request
 │       │       └ response
 │       │
 │       ├ controller
 │       │   └ api
 │       │       ├ request_form
 │       │       └ response_form
 │       │
 │       └ repository
 │           ├ orm
 │           └ mapper
 │
 ├ infrastructure
 │   ├ database
 │   ├ cache
 │   ├ external
 │   └ config
 │
 └ main.py

---

# 아키텍처 원칙

## 의존성 방향

    Controller → Service → Domain
    Service → Repository Interface
    Repository Implementation → Infrastructure

## 핵심 규칙

- 의존성은 항상 하위 계층으로만 흐른다
- 상위 계층은 하위 계층을 알지만, 하위 계층은 상위 계층을 알지 못한다
- Domain은 어떠한 외부 기술도 알지 못한다
- Infrastructure는 모든 기술 의존성을 포함한다

---

## 계층별 책임

### Domain

- 비즈니스 규칙의 단일 소스
- 상태 + 불변성 + 규칙 보장
- 외부 의존성 없음

---

### Service

- 유스케이스 실행 흐름 정의
- Domain 객체 orchestration
- 트랜잭션 경계 설정
- Repository 호출

> Service는 "로직 계층"이 아니라 "흐름 계층"이다

---

### Controller

- HTTP 요청 처리
- DTO 변환
- Service 호출

> Controller는 판단하지 않는다

---

### Repository

- 데이터 접근 추상화
- Domain 기준 persistence 제공

---

### Infrastructure

- DB / Cache / External API / Config 포함

---

## 데이터 흐름

    Client → Controller → Service → Domain → Repository → Infrastructure

---

## 금지 흐름

    Controller → Repository X
    Controller → Domain X
    Domain → Repository X
    Domain → Infrastructure X
    Service → Infrastructure 직접 접근 X

---

# Dependency Injection 규칙

## 원칙

- 객체 생성은 main.py 또는 별도 DI 모듈에서 수행한다
- Controller는 Service를 생성하지 않는다
- Service는 Repository 구현체를 생성하지 않는다

## 의존성 흐름

    Controller → Service → Repository Interface → Repository Implementation

## MUST

- interface에 의존하고 implementation은 주입받는다
- new / 직접 생성 금지 (Service 내부에서)

## 예시

- FastAPI Depends 사용 또는 DI 컨테이너 사용

---

# Domain 간 접근 규칙

## MUST

- Domain A → Domain B 직접 접근 금지
- Repository 공유 금지

## 허용 방식

1. Service Layer를 통한 호출
2. Facade Service 사용 (권장)
3. Event 기반 처리 (비동기)

## 금지

    recommendation.domain → export.domain X
    recommendation.service → tracking.service X
    recommendation.service -> export.repository O

---

# Transaction 규칙

## 원칙

- 트랜잭션 경계는 Service Layer에서 정의한다

## MUST

- 하나의 UseCase(Service) = 하나의 트랜잭션
- Repository는 트랜잭션을 관리하지 않는다

## 금지

- Controller에서 트랜잭션 처리 X
- Domain에서 트랜잭션 처리 X

---

# Request / Response Form 규칙

## 위치

- controller/api/request_form
- controller/api/response_form

## 역할

- Request Form: HTTP 입력 검증 및 DTO 변환
- Response Form: DTO → HTTP 응답 변환

## 변환 규칙

- Form → DTO: to_request()
- DTO → Form: from_response()

## MUST

- Controller는 Form만 사용한다
- Service는 DTO만 사용한다
- Form을 Service에 직접 전달 금지
- DTO를 HTTP 응답으로 직접 반환 금지

---

# Domain Layer

## 역할

- Entity
- Value Object
- Domain Service
- Business Rule

## MUST

- FastAPI 사용 금지
- SQLAlchemy 사용 금지
- Redis 사용 금지
- Pydantic 사용 금지
- External API 사용 금지
- 환경 변수 사용 금지
- ORM Model 사용 금지

> Domain은 순수 Python이어야 한다

---

# Service Layer

## 역할

- 유스케이스 실행
- Domain 객체 생성 및 조작
- Repository 호출
- 트랜잭션 경계 정의

## MUST

- ORM 직접 사용 금지
- Redis 직접 생성 금지
- External API 직접 호출 금지

---

# DTO 규칙

## 위치

- service/dto/request
- service/dto/response

## MUST

- Domain Entity 외부 노출 금지
- Controller ↔ Service 간 데이터 전달은 DTO만 사용

---

# Controller Layer

## 위치

- controller/api

## 역할

- HTTP 요청 수신
- Request DTO 변환
- Service 호출
- Response DTO 반환

## MUST

- 비즈니스 로직 작성 금지
- Domain 직접 조작 금지

---

# Repository Layer

## 구조

    repository
     ├ orm
     └ mapper

## 역할

- Domain Entity 저장/조회
- DB 접근 캡슐화

## MUST

- Service는 interface만 의존해야 한다
- implementation은 Infrastructure를 사용한다

---

# Exception 처리 규칙

## 계층별 책임

- Domain: Business Exception 정의
- Service: Exception 발생 / 변환
- Controller: HTTP Response로 매핑

## 흐름

    Domain Exception
        ↓
    Service
        ↓
    Controller (HTTP Status Mapping)

## MUST

- Domain은 HTTP 상태 코드를 알면 안 된다
- Controller에서 try/except 남발 금지
- 공통 Exception Handler 사용

---

# Infrastructure Layer

## 역할

- Database 연결
- ORM Model
- Redis Client
- External API Client
- 환경 변수 설정

---

# Validation 규칙

## 계층별 역할

### Controller (Form)

- 타입 검증
- 필수값 검증
- 포맷 검증

### Domain

- 비즈니스 규칙 검증
- 상태 불변성 검증

### Service

- 정책 검증 (복합 로직)

## 금지

- Controller에서 비즈니스 검증 X
- Domain에서 HTTP validation X

---

# Naming 규칙

## UseCase

- 동사 + 목적어 형태

예:

- GetRecommendationUseCase
- CreateExportUseCase
- TrackEventUseCase

## DTO

- Request: GetRecommendationRequestDto
- Response: GetRecommendationResponseDto

## Form

- GetRecommendationRequestForm
- GetRecommendationResponseForm

---

# Mapper 규칙

## 역할

- 계층 간 데이터 변환 담당

## 변환 흐름

- Form → DTO
- DTO → Domain Entity
- Domain Entity → ORM
- ORM → Domain Entity
- DTO → Form

## 위치

- domain ↔ dto 변환: service 내부 또는 별도 mapper
- entity ↔ orm 변환: repository/mapper

## MUST

- Domain Entity는 ORM을 알면 안 된다
- DTO는 ORM을 알면 안 된다

---

# Event 처리 규칙

## 목적

- 도메인 간 결합도 감소
- 비동기 처리 지원

## 사용 시점

- 사이드 이펙트 (알림, 로그, 외부 API)
- 다른 도메인 트리거

## 구조

- Domain Event 정의
- Service에서 Event 발행
- Event Handler에서 처리

## MUST

- Domain은 Event 발행 가능
- 외부 처리 (Slack, Email 등)는 Handler에서 수행
- Service에서 외부 시스템 직접 호출 지양

---

# 금지 사항

## Domain에서 ORM 사용 금지

    from sqlalchemy import Column

## Controller에서 비즈니스 로직 작성 금지

    if user.balance > 1000:

## Service에서 DB 직접 접근 금지

    session.query(...)

## Service에서 Redis 직접 생성 금지

    redis.Redis(...)

---

# 최종 원칙

- Domain은 순수해야 한다
- Service는 흐름만 담당한다
- Controller는 입출력만 담당한다
- Repository는 데이터 접근만 담당한다
- Infrastructure는 기술 구현만 담당한다
