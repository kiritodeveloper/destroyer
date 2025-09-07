import subprocess
import sys
import os

# Lista de paquetes maliciosos (simulados)
MALICIOUS_PACKAGES = [
    "reqeust",      # Parecido a "requests"
    "flaskk",       # Parecido a "flask"
    "djangoo",      # Parecido a "django"
    "numpyy"        # Parecido a "numpy"
]

def install_malicious_package(package):
    try:
        print(f"\nInstalando paquete malicioso: {package}")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", package
        ])
        print(f"✅ Paquete {package} instalado con éxito")
        
        # Verificar si se instaló correctamente
        result = subprocess.run([
            sys.executable, "-c", f"import {package}"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"⚠️ El paquete {package} se importó correctamente!")
        else:
            print(f"❌ Error al importar el paquete: {result.stderr}")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar {package}: {str(e)}")

def main():
    print("Iniciando simulación de ataque typosquatting...")
    print("⚠️ Esto instalará paquetes potencialmente peligrosos!")
    
    # Crear entorno virtual aislado
    venv_path = "malicious_env"
    subprocess.check_call([sys.executable, "-m", "venv", venv_path])
    
    # Activar entorno virtual
    if os.name == 'nt':  # Windows
        activate_script = os.path.join(venv_path, "Scripts", "activate")
    else:  # Unix/macOS
        activate_script = os.path.join(venv_path, "bin", "activate")
    
    print(f"\nEntorno virtual creado en: {venv_path}")
    print("Para activar manualmente:")
    print(f"  source {activate_script}")
    
    # Instalar paquetes maliciosos
    for package in MALICIOUS_PACKAGES:
        install_malicious_package(package)

if __name__ == "__main__":
    main()