#!/bin/bash

SOURCE_DIR="/path/to/source"                # 로컬 소스 데이터 경로
TARGET_SERVER="10.10.10.152"                # 타겟 서버 IP 주소
TARGET_BASE="/rsync/"                       # 타겟 서버의 기본 디렉토리 경로
PART_SIZE=$((2 * 1024 * 1024 * 1024))       # 각 디렉토리의 최대 크기 2GB
PART_NUM=1                                  # 현재 복사 중인 디렉토리 번호
TOTAL_SIZE=0                                # 현재 디렉토리에 저장된 데이터의 총 크기
LOG_FILE="/var/log/rsync/backup_log.txt"          # 로그 파일 경로

# 로그 파일 초기화 (백업 시작 시)
echo "백업 시작: $(date)" > "$LOG_FILE"

# 각 디렉토리에 데이터를 분할하여 복사
find "$SOURCE_DIR" -type f | while read FILE; do
    FILE_SIZE=$(stat -c%s "$FILE")   # 현재 파일 크기를 바이트 단위로 가져옴

    # 파일 복사 전 로그 기록
    echo "파일 복사 시작: $FILE (크기: $FILE_SIZE 바이트)" >> "$LOG_FILE"

    # 현재 디렉토리의 크기를 초과하면 다음 디렉토리로 이동
    if (( TOTAL_SIZE + FILE_SIZE > PART_SIZE )); then
        PART_NUM=$((PART_NUM + 1))   # 디렉토리 번호 증가
        TOTAL_SIZE=0                 # 새로운 디렉토리의 총 크기 초기화
        echo "디렉토리 변경: ${TARGET_BASE}${PART_NUM}" >> "$LOG_FILE"
    fi

    # 디렉토리 번호가 7을 초과하지 않도록 확인
    if (( PART_NUM > 7 )); then
        echo "모든 디렉토리에 2GB씩 저장이 완료되었습니다." >> "$LOG_FILE"
        break
    fi

    # 타겟 디렉토리 설정
    TARGET_DIR="${TARGET_BASE}${PART_NUM}"

    # 파일 복사
    rsync -avc "$FILE" "${TARGET_SERVER}:${TARGET_DIR}" >> "$LOG_FILE" 2>&1

    # 복사 성공 여부 확인
    if [ $? -eq 0 ]; then
        echo "파일 복사 완료: $FILE" >> "$LOG_FILE"
    else
        echo "파일 복사 실패: $FILE" >> "$LOG_FILE"
    fi

    # 디렉토리의 총 크기를 업데이트
    TOTAL_SIZE=$((TOTAL_SIZE + FILE_SIZE))
done

# 백업 종료 로그 기록
echo "백업 종료: $(date)" >> "$LOG_FILE"
