#!/bin/bash

# 로그 경로 변수 정의
log_path="/root/uploadtest/"
NOW=$(date +"%Y%m%d")

# 로그 파일 생성 및 업로드 시작 기록
echo "=====================================" >> "$log_path/${NOW}_upload.lst"
echo "upload oci archive storage" >> "$log_path/${NOW}_upload.lst"
echo "Date             = $(date)" >> "$log_path/${NOW}_upload.lst"
echo "=====================================" >> "$log_path/${NOW}_upload.lst"

# OCI Archive Storage에 bulk upload 실행
time /root/bin/oci os object bulk-upload \
  --bucket-name kdg-dku-archive \
  -ns cnpoadfyk0ca \
  --disable-parallel-uploads \
  --object-prefix "${NOW}/" \
  --src-dir /root/uploadsample \
  --no-overwrite >> "$log_path/${NOW}_upload.lst" 2>&1

# 업로드 상태 코드 확인
upload_status=$?
echo "------------------------------------" >> "$log_path/${NOW}_upload.lst"
echo "Upload Status Code: $upload_status" >> "$log_path/${NOW}_upload.lst"

# 업로드 실패 시 이메일 전송
if [ $upload_status -ne 0 ]; then
    # 실패한 파일 목록 추출 (중복 제거)
    failed_files=$(grep -oP 'Uploading parts for \S+' "$log_path/${NOW}_upload.lst" | awk '{print $4}' | sort | uniq)

    # 실패한 파일 목록 디버깅 출력
    echo "Debugging - Failed Files: $failed_files" >> "$log_path/${NOW}_upload.lst"

    # 실패한 파일 목록이 있을 경우 메일로 전송
    if [ -n "$failed_files" ]; then
        echo "OCI CLI upload failed for /root/uploadsample. Failed files: $failed_files" | mail -s "OCI Upload Failure" dogyeong.kim@idatabank.com
    else
        # 실패한 파일이 없으면 일반적인 실패 메시지 전송
        echo "OCI CLI upload failed for /root/uploadsample. No specific failed files found." | mail -s "OCI Upload Failure" dogyeong.kim@idatabank.com
    fi

    echo "sending mail" >> "$log_path/${NOW}_upload.lst"
else
    echo "OCI CLI upload successful for /root/uploadsample" >> "$log_path/${NOW}_upload.lst"
fi

echo "------------------------------------" >> "$log_path/${NOW}_upload.lst"

# 업로드 완료 기록
echo "=====================================" >> "$log_path/${NOW}_upload.lst"
echo "OCI upload Done" >> "$log_path/${NOW}_upload.lst"
echo "Date             = $(date)" >> "$log_path/${NOW}_upload.lst"
echo "=====================================" >> "$log_path/${NOW}_upload.lst"

