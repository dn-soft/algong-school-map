# 알공 계약학교 지도

알공 계약학교 · 무료체험 학교를 대한민국 지도에 표시하는 웹앱.

**Live**: (GitHub Pages 배포 후 URL 업데이트)

## 기능

- 클러스터 뷰 / 포인트 뷰 전환
- 계약학교 / 무료체험 레이어 토글
- 교육청별, 년도별, 학교명/지역 검색 필터
- 밝은(White) / 일반(Green) 지도 스타일 전환
- 학교당 실제 위치 좌표 (Nominatim + Kakao Local API 지오코딩)

## 자동 업데이트

GitHub Actions가 **매일 KST 03:00**에 자동 실행:
1. MongoDB에서 최신 학교 목록 조회
2. 신규 학교만 Kakao API로 지오코딩 (캐시 `coords_cache.json` 활용)
3. `index.html` 재생성
4. 변경사항이 있으면 자동 커밋 → GitHub Pages 자동 재배포

수동 실행: Actions 탭 → Rebuild school map → Run workflow

## 로컬 개발

```bash
# 1. build
export MONGO_API_KEY=Dnsoft@312
export KAKAO_REST_KEY=<kakao_rest_api_key>
python3 build.py

# 2. serve
python3 -m http.server 8765
open http://localhost:8765/index.html
```

## Secrets 설정

GitHub 레포 > Settings > Secrets and variables > Actions에 등록:
- `MONGO_API_KEY`: MongoDB REST API 키
- `KAKAO_REST_KEY`: Kakao REST API 키

## 파일 구조

```
├── build.py              # 빌드 스크립트 (DB 조회 + 지오코딩 + HTML 생성)
├── template.html         # HTML 템플릿 (플레이스홀더 포함)
├── index.html            # 빌드 결과물 (자동 생성)
├── coords_cache.json     # 지오코딩 결과 캐시 (신규 학교만 재지오코딩)
└── .github/workflows/
    └── rebuild.yml       # 매일 자동 재빌드
```
