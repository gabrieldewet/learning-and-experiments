#!/usr/bin/env sh
#
# Build and run the example Docker image.

if [ -t 1 ]; then
    INTERACTIVE="-it"
else
    INTERACTIVE=""
fi

docker build \
    --platform linux/amd64 \
    --secret id=aws_credentials,src=$HOME/.aws/credentials \
    -t ocr-async-api .

docker run \
    -v \
    --rm \
    --publish 8001:8001 \
    $INTERACTIVE \
    ocr-async-api \
    "$@"