FROM python:3.11-slim

WORKDIR /app

# --- build tool‑chain so FMPy can compile the FMU sources ---------------
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential cmake && \
    rm -rf /var/lib/apt/lists/*

# --- Python dependencies -------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- copy Flask app & FMUs ----------------------------------------------
COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
