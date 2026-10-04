FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends --only-upgrade libpcre2-8-0 && rm -rf /var/lib/apt/lists/*
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Utilisateur non-root (principe du moindre privilege)
RUN groupadd --gid 10001 appgroup \
    && useradd --uid 10001 --gid appgroup --no-create-home --shell /usr/sbin/nologin appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=appuser:appgroup . .

# Collecte des fichiers statiques (CSS admin, etc.)
RUN python manage.py collectstatic --noinput

USER 10001
EXPOSE 8000

# Verification de sante sans curl (moins de surface d attaque)
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/healthz/').status==200 else 1)"

# Serveur de production gunicorn (jamais runserver)
CMD ["gunicorn", "huawei.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-"]
