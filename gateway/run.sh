#!/bin/bash

echo "{
    \"thingsboard\": {
        \"broker\": \"${TB_BROKER}\",
        \"port\": ${TB_PORT}
    },
    \"socketserver\": {
        \"host\": \"${SOCK_ADDRESS}\",
        \"port\": ${SOCK_PORT},
        \"threading\": ${SOCK_THREADING}
    }
}" > /app/config.json

python -u thingsboard.py