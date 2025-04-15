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

# [Previous Dockerfile content remains the same until the compilation step]

# Compile models
RUN for model in FirstOrder SecondOrderSystem; do \
      if [ -f "$model.mo" ]; then \
        omc --simCodeTarget=fmu "$model.mo" && \
        mv "$model.fmu" /app/output/; \
      fi; \
    done && \
    mkdir -p /app/output

# [Rest of Dockerfile remains the same]

# Copy remaining application files
COPY . .

# Set the output directory as a volume
VOLUME /app/output

CMD ["python3", "app.py"]
