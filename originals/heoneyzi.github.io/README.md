# Jiheon Kang · 강지헌

Biomedical AI research portfolio for **https://heoneyzi.github.io/**.

연세대학교 전기전자공학부 학부 연구자 강지헌의 연구, 논문, 프로젝트, 활동을 소개하는 한국어/영어 홈페이지입니다.

## GitHub Pages 게시

1. `heoneyzi` 계정에서 **heoneyzi.github.io**라는 public 저장소를 만듭니다.
2. 이 폴더의 파일을 저장소의 `main` 브랜치 최상위에 업로드합니다.
3. 저장소 **Settings → Pages → Build and deployment**에서 **Deploy from a branch**, **main**, `/ (root)`를 선택하고 저장합니다.
4. GitHub의 Pages 배포 완료 후 [홈페이지](https://heoneyzi.github.io/)에서 확인합니다.

별도의 서버, Node.js 설치, API 키, 유료 서비스가 필요하지 않은 HTML/CSS/JavaScript 정적 사이트입니다. `.nojekyll`은 Jekyll 처리를 생략하도록 지정합니다.

## 수정하기

- `index.html`: 모든 영어 본문과 한국어 번역(`data-ko` 속성), 논문·프로젝트 링크
- `styles.css`: 색상·글꼴·반응형 레이아웃·인쇄 레이아웃
- `script.js`: 한국어/영어 전환 및 선택 언어 저장
- `Jiheon_Kang_CV.pdf`: 다운로드 가능한 전체 CV. 새 CV로 교체해도 파일명은 유지하세요.
- `gdtr-context-separation.png`: TDiG 후속 분석 그림
- `favicon.svg`: 홈페이지 아이콘
- `robots.txt`, `sitemap.xml`: 검색엔진 탐색 설정

로컬 미리보기: 이 폴더에서 `python3 -m http.server 4173 --bind 127.0.0.1` 실행 후 http://127.0.0.1:4173/ 접속.

## 내용과 출처

2026년 9월 CV를 기준으로 작성했습니다. 논문 저자·역할·수치·연락처는 CV를 따릅니다. 추가 소개문은 해당 경력을 바탕으로 편집했습니다. GitHub 공개 저장소를 연결했으며 fork는 구분했습니다.

- GDTR: ICML 2026 GenBio **워크숍** Oral 채택. 메인 컨퍼런스 논문으로 표현하지 않습니다.
- Virtual Cell Challenge: Jiang24 IFNG/BxPC3의 **공개 프록시 PDS 0.5794**. 공식 리더보드 점수가 아닙니다.
- CAFA 6: 224,309개는 **테스트 상위집합** 단백질 수입니다.
- PhenoFocus: 31개 화합물 HDAC 스크린에서 얻은 **초기 MVP** 결과입니다.
- TDiG 그림은 GDTR 이후의 별도 후속 분석입니다. [원본 프로젝트](https://github.com/YAICON-8th-Think-Deep-in-Genome/TDiG).

JavaScript가 꺼져 있어도 영어 본문·탐색·CV 링크·연구 노트가 동작합니다. 언어 설정만 브라우저에 저장하며 방문자 데이터 수집이나 외부 분석 스크립트는 없습니다.
