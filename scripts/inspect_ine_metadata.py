import requests
import json

TABLE_ID = "33784"
BASE_URL = "https://servicios.ine.es/wstempus/js/es"

def get_variable_values(var_id):
    url = f"{BASE_URL}/VALORES_VARIABLE/{TABLE_ID}/{var_id}"
    print(f"Fetching {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"Variable {var_id}: Found {len(data)} values.")
        # Print first 5 values as sample
        print(json.dumps(data[:5], indent=2, ensure_ascii=False))
        return data
    except Exception as e:
        print(f"Error fetching variable {var_id}: {e}")
        return []

if __name__ == "__main__":
    # 96192: Sexo
    # 96193: Municipios
    # 96194: Nacionalidad
    
    print("--- SEXO (96192) ---")
    get_variable_values(96192)
    
    print("\n--- NACIONALIDAD (96194) ---")
    get_variable_values(96194)
    
    print("\n--- MUNICIPIOS (96193) sample ---")
    get_variable_values(96193)
