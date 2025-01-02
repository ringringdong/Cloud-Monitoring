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
  --no-overwrite >> "$log_path/${NOW}_upload.lst"

  # 업로드 완료 기록
echo "=====================================" >> "$log_path/${NOW}_upload.lst"
echo "OCI upload Done" >> "$log_path/${NOW}_upload.lst"
echo "Date             = $(date)" >> "$log_path/${NOW}_upload.lst"
echo "=====================================" >> "$log_path/${NOW}_upload.lst"

