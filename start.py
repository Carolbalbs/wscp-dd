import os
import uvicorn
import subprocess
import time
import sys

def main():
    print("--- PubChem Search Version Manager ---")
    print("1. Iniciar v1 (Busca Simples - Porta 8001)")
    print("2. Iniciar v2 (Busca Avançada - Porta 8000)")
    print("3. Sair")
    
    choice = input("\nEscolha a versão (1/2/3): ")
    
    if choice == '1':
        print("\nIniciando v1 na porta 8001...")
        subprocess.run([sys.executable, "v1/main.py"])
    elif choice == '2':
        print("\nIniciando v2 na porta 8000...")
        subprocess.run([sys.executable, "v2/main.py"])
    else:
        print("Saindo...")

if __name__ == "__main__":
    main()
