# Use the same image so fmpy has a full GNU tool‑chain
FROM openmodelica/openmodelica:v1.25.0-ompython

WORKDIR /app

# ---------- Python dependencies ----------
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# ---------- copy the Flask project (FMUs included) ----------
COPY . .

EXPOSE 5000
CMD ["python3", "app.py"]
