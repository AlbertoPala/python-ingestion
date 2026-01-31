import requests
import sys
import logging

# Configurar logging para que se muestre en stdout (que Dataproc captura y envía a Airflow)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_test():
    logger.info("Iniciando test de conectividad externa...")
    url = "https://httpbin.org/get"
    
    try:
        logger.info(f"Enviando request a {url}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        logger.info(f"Success! Status Code: {response.status_code}")
        logger.info(f"Response Body: {response.json()}")
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
