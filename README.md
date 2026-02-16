# TinyQR (URL Shortener + QR)

## What
긴 URL을 짧은 코드로 저장하고, 나중에 해당 코드로 접속하면 원본 URL로 이동(리다이렉트)시키는 서비스.

## AWS (현재까지)
- DynamoDB: tinyqr_links (code -> url 저장)
- Lambda: tinyqr_create (단축 코드 생성 + DynamoDB 저장)

## Today Done
- DynamoDB 테이블 생성
- Lambda 함수 생성
- 콘솔 테스트로 PutItem 성공
- DynamoDB에 저장된 item 확인 완료

## Next
- API Gateway 연결: POST /shorten
- 리다이렉트용 Lambda: GET /{code} -> 302
- 프론트에서 QR 생성
