import requests
import sys

def run_test():
    print("Iniciando test de conectividad externa...")
    url = "https://httpbin.org/get"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"Success! Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
