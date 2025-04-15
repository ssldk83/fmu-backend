# Install OpenModelica
FROM openmodelica/openmodelica:v1.24.5-ompython

# Copy your model files
COPY YourModel.mo /app/
WORKDIR /app

# Compile the model
RUN omc +target=linux64 +simCodeTarget=fmu YourModel.mo

# Set up your Python environment
RUN apt-get install -y python3-pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python3", "app.py"]
