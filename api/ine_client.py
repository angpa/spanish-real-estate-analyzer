import requests
import json
from datetime import datetime

class INEClient:
    BASE_URL = "https://servicios.ine.es/wstempus/js/es"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False # DEBUG: Disable SSL verification
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

    def get_variable_values(self, table_id, variable_id):
        """Fetch all possible values for a variable (e.g., all municipalities)."""
        url = f"{self.BASE_URL}/VALORES_VARIABLE/{table_id}/{variable_id}"
        print(f"DEBUG: Fetching {url}...")
        try:
            response = self.session.get(url, timeout=10)
            print(f"DEBUG: Status {response.status_code}")
            print(f"DEBUG: Headers: {response.headers}")
            print(f"DEBUG: Content Preview: {response.text[:200]}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching variable {variable_id}: {e}")
            return []

    def get_data(self, table_id, params):
        """Fetch data for a specific table with filters."""
        url = f"{self.BASE_URL}/DATOS_TABLA/{table_id}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching data for table {table_id}: {e}")
            return []

    STATIC_MUNICIPALITIES = [
        {"Id": "46078", "Nombre": "Burjassot", "Slug": "burjassot"}, # Added as priority
        {"Id": "28079", "Nombre": "Madrid", "Slug": "madrid"},
        {"Id": "08019", "Nombre": "Barcelona", "Slug": "barcelona"},
        {"Id": "46250", "Nombre": "Valencia", "Slug": "valencia"},
        {"Id": "41091", "Nombre": "Sevilla", "Slug": "sevilla"},
        {"Id": "50297", "Nombre": "Zaragoza", "Slug": "zaragoza"},
        {"Id": "29067", "Nombre": "Málaga", "Slug": "malaga"},
        {"Id": "30030", "Nombre": "Murcia", "Slug": "murcia"},
        {"Id": "07040", "Nombre": "Palma", "Slug": "palma"},
        {"Id": "35016", "Nombre": "Palmas de Gran Canaria, Las", "Slug": "las-palmas"},
        {"Id": "48020", "Nombre": "Bilbao", "Slug": "bilbao"},
        {"Id": "03014", "Nombre": "Alicante/Alacant", "Slug": "alicante"},
        {"Id": "14021", "Nombre": "Córdoba", "Slug": "cordoba"}
    ]

    def search_municipality(self, query):
        """Search for a municipality by name and return its ID."""
        query_norm = query.lower().strip()
        matches = []
        
        # 1. Try API First
        # Variable 96193 is "Municipios" for table 33784
        try:
            all_municipalities = self.get_variable_values("33784", "96193")
        except Exception:
            all_municipalities = [] # Fallback if API fails
            
        if all_municipalities:
            for muni in all_municipalities:
                name = muni.get("Nombre", "").lower()
                if query_norm in name:
                    matches.append(muni)
        
        # 2. Fallback to Static List if no matches or API failed
        if not matches:
             print(f"DEBUG: No API matches for '{query}', checking static list...")
             for muni in self.STATIC_MUNICIPALITIES:
                 if query_norm in muni["Nombre"].lower() or query_norm in muni["Slug"]:
                     matches.append(muni)

        # Sort by length similarity to prioritize exact matches
        matches.sort(key=lambda x: len(x.get("Nombre", "")))
        return matches

ine_client = INEClient()
