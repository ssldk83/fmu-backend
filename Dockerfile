# ──────────────────────────────────────────────────────────────────────────
# base image: 45 MB compressed – just Debian‑slim + Python 3.11
# ──────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# ---------- Python deps (only pure‑Python wheels) -------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- copy Flask project & FMUs ------------------------------------
COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
