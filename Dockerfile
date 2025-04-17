FROM openmodelica/openmodelica:v1.25.0-ompython

WORKDIR /app

# ---- install python deps -------------------------------------------------
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# ---- copy Modelica sources & pre‑compile FMUs ---------------------------
COPY FirstOrder.mo SecondOrderSystem.mo ./

# compile FMUs; they end up in /app/*.fmu
RUN for m in FirstOrder SecondOrderSystem ; do \
      test -f "$m.mo" && \
      echo "loadFile(\"$m.mo\"); translateModelFMU($m, version=\"2.0\", fmuType=\"me\");" \
      > build.mos && omc build.mos ; \
    done

# ---- copy the rest of the Flask project ---------------------------------
COPY . .

EXPOSE 5000
CMD ["python3", "app.py"]
