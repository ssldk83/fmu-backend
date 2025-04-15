FROM openmodelica/openmodelica:v1.25.0-ompython

WORKDIR /app

# Install Python and pip dependencies
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl && \
    pip3 install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Copy Modelica model files
COPY FirstOrder.mo SecondOrderSystem.mo ./

# Compile FMUs directly into /app so app.py can find them
RUN for model in FirstOrder SecondOrderSystem; do \
      if [ -f "$model.mo" ]; then \
        echo "loadFile(\"$model.mo\"); getErrorString();" > compile.mos && \
        echo "translateModelFMU($model, version=\"2.0\"); getErrorString();" >> compile.mos && \
        omc compile.mos && \
        if [ -f "$model.fmu" ]; then mv "$model.fmu" /app/; fi; \
      fi; \
    done

# Copy the rest of your Flask app
COPY . .

# Run the Flask server
CMD ["python3", "app.py"]
