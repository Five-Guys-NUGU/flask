# Tools

1. Ngrok
2. Flask
3. Firebase
4. firebase-admin

# To do

1. 이미 체크 실행중인데 체크를 하기 원할 때 예외 처리
2. 이미 쉬는 중인데 쉬기를 바랄 때 예외 처리
3. 이미 끝냈는데 끝내거나 쉬기를 바랄 때 예외 처리

# Bug Fix

1. General -> Global 설정 -> Web URL에서 맨 마지막에 "/" 붙여주면 모든 Action이 root로만 가게 된다.

# Reference

1. OAuth 2.0을 구축할 수 없어서 NUGU에서 우리 앱에 로그인 하는 기능은 배제할 것
2. Timer Triging

- start_timer = {
  collection_Subject -> study_status = True
  collection_StudyTimer -> Add document -> start_time = timestamp 등록
  }
- finish_timer = {
  collection_Subject -> study_status = False
  collection_StudyTimer -> 이미 존재하는 document -> finish_time = timestamp 등록
  }

3. Firestore에서 data 가져오는 방법

- Collection -> stream()
- Document -> get()
