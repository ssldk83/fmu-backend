FROM openmodelica/openmodelica:v1.25.0-minimal

WORKDIR /app

# Install Python and dependencies
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl && \
    pip3 install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Copy your Modelica model files
COPY FirstOrder.mo SecondOrderSystem.mo ./

# Compile FMUs (assuming models are fully self-contained)
RUN mkdir -p /app/output && \
    for model in FirstOrder SecondOrderSystem; do \
      if [ -f "$model.mo" ]; then \
        echo "loadFile(\"$model.mo\"); getErrorString();" > compile.mos && \
        echo "translateModelFMU($model, version=\"2.0\"); getErrorString();" >> compile.mos && \
        omc compile.mos && \
        if [ -f "$model.fmu" ]; then mv "$model.fmu" /app/output/; fi; \
      fi; \
    done

# Copy the rest of the Flask backend
COPY . .

# Run the Flask app
CMD ["python3", "app.py"]
