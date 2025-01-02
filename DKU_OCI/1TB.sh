#!/bin/bash

SOURCE_DIR="/path/to/source"                # 로컬 소스 데이터 경로
TARGET_SERVER="10.10.10.152"                # 타겟 서버 IP 주소
TARGET_BASE="/rsync/"                       # 타겟 서버의 기본 디렉토리 경로
PART_SIZE=$((1024 * 1024 * 1024 * 1024))    # 각 디렉토리의 최대 크기 1TB
PART_NUM=1                                  # 현재 복사 중인 디렉토리 번호
TOTAL_SIZE=0                                # 현재 디렉토리에 저장된 데이터의 총 크기

# 각 디렉토리에 데이터를 분할하여 복사
find "$SOURCE_DIR" -type f | while read FILE; do
    FILE_SIZE=$(stat -c%s "$FILE")   # 현재 파일 크기를 바이트 단위로 가져옴

    # 현재 디렉토리의 크기를 초과하면 다음 디렉토리로 이동
    if (( TOTAL_SIZE + FILE_SIZE > PART_SIZE )); then
        PART_NUM=$((PART_NUM + 1))   # 디렉토리 번호 증가
        TOTAL_SIZE=0                 # 새로운 디렉토리의 총 크기 초기화
    fi

    # 디렉토리 번호가 7을 초과하지 않도록 확인
    if (( PART_NUM > 7 )); then
        echo "모든 디렉토리에 1TB씩 저장이 완료되었습니다."
        break
    fi

    # 타겟 디렉토리 설정
    TARGET_DIR="${TARGET_BASE}${PART_NUM}"

    # 파일 복사
    rsync -avc "$FILE" "${TARGET_SERVER}:${TARGET_DIR}"

    # 디렉토리의 총 크기를 업데이트
    TOTAL_SIZE=$((TOTAL_SIZE + FILE_SIZE))
done
