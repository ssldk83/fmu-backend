FROM openmodelica/openmodelica:v1.25.0-ompython

WORKDIR /app

# ---- system packages needed for FMPy source‑build (gcc, make, cmake) ----
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential cmake && \
    rm -rf /var/lib/apt/lists/*

# ---- Python deps ----
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# ---- application code (FMUs included) ----
COPY . .

EXPOSE 5000
CMD ["python3", "app.py"]
