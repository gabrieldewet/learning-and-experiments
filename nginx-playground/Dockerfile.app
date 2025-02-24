FROM python:3.11-slim-buster
COPY --from=ghcr.io/astral-sh/uv:0.6.2 /uv /uvx /bin/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0


# Create app directory
WORKDIR /app

# Copy project
COPY . /app/

# Install python dependencies using uv
RUN /root/.local/bin/uv pip install --no-cache-dir -r requirements.txt



# Collect static files
RUN python manage.py collectstatic --noinput

# Migrate
RUN python manage.py migrate

# Create super user
RUN python manage.py createsuperuser

# Set up Nginx configuration
COPY nginx/myproject.conf /etc/nginx/conf.d/default.conf

# Set up Gunicorn
CMD gunicorn --bind unix:/run/gunicorn.sock --workers 3 --user www-data --group www-data myproject.wsgi:application

# Expose port 80 for Nginx
EXPOSE 80
