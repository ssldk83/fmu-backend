# Use the official OpenModelica image
FROM openmodelica/openmodelica:v1.25.0-ompython

# Set working directory
WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Copy model files
COPY *.mo ./

# Compile models (combined into one RUN for better layer caching)
RUN for model in FirstOrder SecondOrderSystem; do \
      if [ -f "$model.mo" ]; then \
        omc +target=linux64 +simCodeTarget=fmu "$model.mo" && \
        mv "$model.fmu" /app/output/; \
      fi; \
    done && \
    mkdir -p /app/output

# Copy remaining application files
COPY . .

# Set the output directory as a volume
VOLUME /app/output

CMD ["python3", "app.py"]
