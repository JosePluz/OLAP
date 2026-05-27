#!/usr/bin/env python
"""
OLAP Dashboard - Quick Start Script
Ejecuta automáticamente la configuración y el dashboard
"""

import subprocess
import sys
import time

def main():
    print("""
         OLAP - Anime & Manga Analytics Dashboard           
              Sistema de Toma de Decisiones Basado en Datos     
    """)
    
    # Paso 1: Setup de BD
    print("\n[1/3]  Preparando base de datos...")
    try:
        result = subprocess.run(
            [sys.executable, "setup_database.py"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error en setup: {e.stderr}")
        sys.exit(1)
    
    # Paso 2: Verificar dependencias
    print("\n[2/3]  Verificando dependencias...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"],
            check=True
        )
        print(" Dependencias listas")
    except subprocess.CalledProcessError as e:
        print(f"Error instalando dependencias: {e}")
        sys.exit(1)
    
    # Paso 3: Ejecutar dashboard
    print("\n[3/3] Iniciando dashboard...")
    print("""
  El dashboard estará disponible en: http://localhost:8501     
                                                                
  Cierra esta ventana o presiona Ctrl+C para detener           
    """)
    
    time.sleep(1)
    
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "dashboard.py"],
            check=False
        )
    except KeyboardInterrupt:
        print("\n\n Dashboard cerrado")
        sys.exit(0)

if __name__ == "__main__":
    main()
