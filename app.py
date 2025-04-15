FROM openmodelica/openmodelica:v1.25.0-minimal

WORKDIR /app

# Install Python and dependencies
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl && \
    pip3 install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Copy Modelica model files
COPY FirstOrder.mo SecondOrderSystem.mo ./

# Compile FMUs with logging
RUN mkdir -p /app/output && \
    for model in FirstOrder SecondOrderSystem; do \
      if [ -f "$model.mo" ]; then \
        echo "loadFile(\"$model.mo\"); getErrorString();" > compile.mos && \
        echo "translateModelFMU($model, version=\"2.0\"); getErrorString();" >> compile.mos && \
        omc compile.mos > compile.log 2>&1 && \
        echo "====== compile.log for $model ======" && cat compile.log && \
        if [ -f "$model.fmu" ]; then \
          echo "$model.fmu generated successfully"; \
          mv "$model.fmu" /app/output/; \
        else \
          echo "ERROR: $model.fmu NOT generated"; \
          cat compile.log; \
          exit 1; \
        fi; \
      else \
        echo "ERROR: $model.mo not found"; \
        exit 1; \
      fi; \
    done

# Copy the rest of the Flask backend (app.py, etc.)
COPY . .

# Run the Flask app
CMD ["python3", "app.py"]
