FROM openmodelica/openmodelica:v1.25.0-minimal

WORKDIR /app

# Install Python and dependencies
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Copy Modelica model files
COPY *.mo ./

# Install Modelica Standard Library
RUN echo "installPackage(Modelica); getErrorString();" | omc

# Compile models to FMUs
RUN mkdir -p /app/output && \
    for model in FirstOrder SecondOrderSystem; do \
      if [ -f "$model.mo" ]; then \
        echo "loadFile(\"$model.mo\"); loadModel(Modelica); getErrorString();" > compile.mos && \
        echo "translateModelFMU($model, version=\"2.0\"); getErrorString();" >> compile.mos && \
        omc compile.mos && \
        mv $model.fmu /app/output/; \
      fi; \
    done

# Copy remaining application files (Flask backend etc.)
COPY . .

CMD ["python3", "app.py"]
