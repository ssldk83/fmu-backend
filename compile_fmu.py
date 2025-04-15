import subprocess
import os
import glob

def compile_modelica_model(filename):
    model_name = os.path.splitext(os.path.basename(filename))[0]
    omc_cmd = f'echo "buildModelFMU({model_name})" | omc -'
    result = subprocess.run(omc_cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error compiling {filename}: {result.stderr}")
        return

    # Move FMU if created
    fmu_candidates = glob.glob(f"{model_name}.fmu")
    for fmu in fmu_candidates:
        print(f"✅ Generated: {fmu}")
        os.rename(fmu, f"./{fmu}")

if __name__ == "__main__":
    for mo_file in glob.glob("*.mo"):
        print(f"🔧 Compiling {mo_file}")
        compile_modelica_model(mo_file)
