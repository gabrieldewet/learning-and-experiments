#!/usr/bin/env bash

celery -A ocr_api worker -l info
