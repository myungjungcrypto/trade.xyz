# Crude Oil 누적 펀딩 계산기 구현 계획

## 목표
Crude Oil(WTI/Brent) perpetual futures의 누적 펀딩비(cumulative funding rate)를 계산하는 도구 구현

## 구현 단계

### 1단계: 프로젝트 초기 설정
- TypeScript + Node.js 프로젝트 초기화 (`package.json`, `tsconfig.json`)
- 필요 패키지: `axios` (API 호출), `ethers` (온체인 데이터 조회 시), `dotenv`

### 2단계: 데이터 소스 연동
- DEX/CEX에서 crude oil perpetual의 펀딩 레이트 데이터 수집
  - 가능한 소스: Synthetix, GMX, dYdX, Kwenta 등 (crude oil perp 지원하는 프로토콜)
  - 또는 CEX API (Binance, Bybit 등에서 oil 관련 perp 펀딩 데이터)
- API 클라이언트 모듈 작성 (`src/api/`)

### 3단계: 펀딩 레이트 계산 로직
- `src/funding/calculator.ts` 생성
  - 개별 펀딩 레이트 수집
  - 누적 펀딩 = Σ(각 기간별 funding rate)
  - 시간 구간별 누적 (1h, 8h, daily, weekly, monthly)
- 연율화(annualized) 펀딩 레이트 계산

### 4단계: 데이터 저장 및 이력 관리
- 펀딩 레이트 이력 저장 (JSON 파일 또는 SQLite)
- 과거 데이터 조회 기능

### 5단계: 출력 및 표시
- CLI 출력: 현재 펀딩 레이트, 누적 펀딩, 연율화 수치
- 선택적: 차트/그래프 출력

## 파일 구조 (예상)
```
src/
├── index.ts              # 진입점
├── api/
│   └── client.ts         # 데이터 소스 API 클라이언트
├── funding/
│   ├── calculator.ts     # 누적 펀딩 계산 로직
│   └── types.ts          # 타입 정의
├── storage/
│   └── history.ts        # 이력 저장/조회
└── utils/
    └── format.ts         # 출력 포맷팅
```

## 핵심 질문 (구현 전 확인 필요)
1. 어떤 거래소/프로토콜의 crude oil perp 데이터를 사용할지?
2. 온체인(DeFi) vs 오프체인(CEX) 중 어디서 데이터를 가져올지?
3. 실시간 모니터링이 필요한지, 일회성 계산인지?
