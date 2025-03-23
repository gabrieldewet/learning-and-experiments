
#!/usr/bin/env sh
#
# Build and run the example Docker image.

if [ -t 1 ]; then
    INTERACTIVE="-it"
else
    INTERACTIVE=""
fi

docker build -t ocr-async-api .

docker run \
    -v \
    --rm \
    --publish 8001:8001 \
    $INTERACTIVE \
    ocr-async-api \
    "$@"
