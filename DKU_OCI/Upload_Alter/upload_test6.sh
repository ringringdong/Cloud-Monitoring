#!/bin/bash

NAMESPACE="cnpoadfyk0ca"
BUCKET_NAME="ilsan-bucket"
BASE_DIR="/nasbackup/backupLT40"
LOG_FILE="/var/log/oci_upload_lt_09_to_12.log"
EMAIL="admin@example.com"  # 이메일 수신자 주소 설정

FOLDERS=("LT09" "LT10" "LT11" "LT12")

echo "OCI Upload Log - $(date)" > "$LOG_FILE"
echo "-------------------------------------------" >> "$LOG_FILE"

for folder in "${FOLDERS[@]}"; do
    SRC_DIR="$BASE_DIR/$folder"
    START_TIME=$(date "+%Y-%m-%d %H:%M:%S")
    echo "${START_TIME} Starting upload for $SRC_DIR..." | tee -a "$LOG_FILE"

    oci os object bulk-upload -ns "$NAMESPACE" -bn "$BUCKET_NAME" --src-dir "$SRC_DIR" --prefix "$folder/"

    if [ $? -eq 0 ]; then
        END_TIME=$(date "+%Y-%m-%d %H:%M:%S")
        echo "[${END_TIME}] Successfully uploaded $SRC_DIR to $BUCKET_NAME/$folder/" | tee -a "$LOG_FILE"
    else
        END_TIME=$(date "+%Y-%m-%d %H:%M:%S")
        echo "[${END_TIME}] Failed to upload $SRC_DIR" | tee -a "$LOG_FILE"

        # 이메일 내용 작성 및 전송
        EMAIL_SUBJECT="[ERROR] OCI Upload Failed for $folder"
        EMAIL_BODY="Upload for folder $folder ($SRC_DIR) failed at $END_TIME. Check the log at $LOG_FILE for details."
        echo -e "Subject: $EMAIL_SUBJECT\n\n$EMAIL_BODY" | sendmail "$EMAIL"

        # mailx를 사용하는 경우
        # echo "$EMAIL_BODY" | mailx -s "$EMAIL_SUBJECT" "$EMAIL"
    fi
    echo "-------------------------------------------" >> "$LOG_FILE"
done
