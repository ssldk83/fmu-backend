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

# Compile FMUs from .mo files using Python
RUN python3 compile_fmu.py

# Copy the rest of your Flask app
COPY . .

# Run the Flask server
CMD ["python3", "app.py"]
