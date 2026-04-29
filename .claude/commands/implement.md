# 목적

사용자가 Backlog와 Todo를 입력하면
해당 Backlog를 구현하기 위한 코드를 생성한다.

이 Command는 다음을 수행한다.

- Backlog Title을 이해한다
- Success Criteria를 구현 기준으로 사용한다
- Todo 목록을 기반으로 구현 단계를 수행한다
- 실제 동작 가능한 코드를 생성한다

---

# 중요 규칙 (Strict)

이 Command는 Backlog 구현 명령이다.

다음 항목을 생성하지 않는다.

- Given
- When
- Then
- Scenario
- Test Case
- Architecture 설계
- Component specification
- Props 정의 문서
- API 설계 문서

이 Command는 문서를 생성하지 않는다.

반드시 코드 구현 결과만 생성한다.

---

# 사용 방법

```
/implement
```

---

# 입력 예시

**Backlog**

애플리케이션이 시작 시 .env 환경 변수를 로드한다

**Success Criteria**

- 애플리케이션이 시작될 때 .env 파일에서 필요한 환경 변수를 읽는다
- 필수 환경 변수가 존재하지 않으면 오류를 발생시킨다
- 환경 변수 값이 애플리케이션 전역에서 접근 가능하다
- 환경 변수가 정상적으로 로드되면 애플리케이션이 정상 실행된다

**Todo**

- 필수 환경 변수 목록을 정의한다
- 환경 변수 로드 및 검증 로직을 구현한다
- 환경 변수 누락 시 오류 발생 처리를 구현한다
- 환경 변수를 전역에서 접근 가능하도록 제공한다
- 환경 변수 로드 결과를 확인할 수 있도록 구현한다

---

# 동작 규칙

- Backlog Title을 읽는다
- Success Criteria를 구현 기준으로 사용한다
- Todo 목록을 구현 순서로 사용한다
- Todo 단위로 코드를 생성한다
- 실제 동작 가능한 코드만 생성한다

---

# 출력 형식

**Implementation**

설명 없이 코드만 출력한다.

코드는 다음 형식을 따른다.

```
파일 경로
코드 블록
```

**예**

`src/config/env.ts`

```typescript
export const env = {
  PORT: process.env.PORT,
  DATABASE_URL: process.env.DATABASE_URL
}
```
