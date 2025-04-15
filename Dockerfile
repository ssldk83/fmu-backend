FROM openmodelica/openmodelica:v1.25.0-ompython

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Copy model files
COPY *.mo ./

# Verify OpenModelica version
RUN omc --version

# Compile models to FMUs
RUN for model in FirstOrder SecondOrderSystem; do \
      if [ -f "$model.mo" ]; then \
        echo "loadModel(Modelica); getErrorString();" > compile.mos && \
        echo "translateModelFMU($model, version=\"2.0\"); getErrorString();" >> compile.mos && \
        omc compile.mos && \
        mv $model.fmu /app/output/; \
      fi; \
    done && \
    mkdir -p /app/output

# Copy remaining application files
COPY . .

CMD ["python3", "app.py"]
