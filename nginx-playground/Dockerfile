FROM python:3.11-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    curl \  # Add curl to download uv \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -fsSL https://raw.githubusercontent.com/astral-sh/uv/main/install.sh | sh

# Create app directory
WORKDIR /app

# Install python dependencies using uv
COPY requirements.txt /app/
RUN /root/.local/bin/uv pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Set up Nginx configuration
COPY nginx/myproject.conf /etc/nginx/conf.d/default.conf

# Set up Gunicorn
CMD gunicorn --bind unix:/run/gunicorn.sock --workers 3 --user www-data --group www-data myproject.wsgi:application

# Expose port 80 for Nginx
EXPOSE 80
