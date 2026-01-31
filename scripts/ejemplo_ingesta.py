import pandas as pd
import requests
import sys
import os

def run_ingestion():
    print("Iniciando ingesta de datos de ejemplo...")
    
    # URL de API pública para pruebas
    url = "https://jsonplaceholder.typicode.com/posts"
    
    try:
        print(f"Consultando API: {url}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        print(f"Se obtuvieron {len(df)} registros.")
        
        # Transformación simple
        print("Realizando transformación de datos...")
        df['title_capitalized'] = df['title'].str.upper()
        df['body_length'] = df['body'].str.len()
        
        # Mostrar resultados
        print("Primeros 5 registros transformados:")
        print(df[['id', 'title_capitalized', 'body_length']].head())
        
        print("Proceso finalizado correctamente.")
        
    except Exception as e:
        print(f"Error durante el proceso: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_ingestion()
