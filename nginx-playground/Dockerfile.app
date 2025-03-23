FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

# Create app directory
WORKDIR /app

# Copy project
COPY . /app/

RUN apt-get update && apt-get install -y nginx

# Install python dependencies using uv
RUN rm -rf .venv
RUN uv venv
ENV PATH="/app/.venv/bin:$PATH"
RUN uv pip install --no-cache-dir -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --noinput

# Migrate
RUN python manage.py migrate

# Create super user
# RUN python manage.py createsuperuser

# Copy Nginx config
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Expose port 80 for Nginx
EXPOSE 80

# Set up Gunicorn
CMD service nginx start && gunicorn --bind unix:/run/django-app.sock --workers 1 watch-list.wsgi:application
