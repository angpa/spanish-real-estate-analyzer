from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
import sys
import os

# Add current directory to path so we can import local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from ine_client import ine_client
except ImportError:
    # Fallback for Vercel environment where imports might be different
    from api.ine_client import ine_client

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        municipality_query = query_params.get('municipality', [None])[0]

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        if not municipality_query:
            self.wfile.write(json.dumps({"error": "Missing 'municipality' parameter"}).encode('utf-8'))
            return

        try:
            # 1. Search for Municipality
            matches = ine_client.search_municipality(municipality_query)
            
            if not matches:
                self.wfile.write(json.dumps({"error": f"No municipality found for '{municipality_query}'"}).encode('utf-8'))
                return
            
            # Use the best match
            selected_muni = matches[0]
            muni_id = selected_muni.get("Id")
            muni_name = selected_muni.get("Nombre")

            # 2. Fetch Data
            # Try API first, if fails and we have static mock data, use it.
            try:
                 # Real API Call logic
                 req_params = {"tv": f"96193:{muni_id}", "date": "20230101"}
                 print(f"DEBUG: Requesting data for {muni_name} (ID: {muni_id})")
                 data_rows = ine_client.get_data("33784", req_params)
                 
                 if not data_rows:
                     raise Exception("No data returned from API")
                     
                 # Process Real Data (Same logic as before)
                 pop_total = 0
                 pop_spanish = 0
                 pop_foreign = 0
                 breakdown = []

                 for row in data_rows:
                    name = row.get("Nombre", "")
                    latest_value = 0
                    if row.get("Data"):
                        sorted_data = sorted(row["Data"], key=lambda x: x.get("Fecha", 0), reverse=True)
                        if sorted_data:
                            latest_value = sorted_data[0].get("Valor", 0)

                    if "Española" in name and "Total" in name.split(".")[0]:
                         pop_spanish = latest_value
                    elif "Extranjera" in name and "Total" in name.split(".")[0]:
                         pop_foreign = latest_value
                    elif "Total" in name and "Total" in name.split(".")[0] and "Española" not in name and "Extranjera" not in name:
                         pop_total = latest_value
                    
                    if "Total" in name.split(".")[0] and "Española" not in name and "Extranjera" not in name and "Total" not in name.split(".")[-2]:
                         nat_name = name.split(".")[-2].strip()
                         if nat_name and nat_name != "Total" and latest_value > 0:
                             breakdown.append({"name": nat_name, "value": latest_value})

                 breakdown.sort(key=lambda x: x["value"], reverse=True)
                 top_breakdown = breakdown[:10]

                 response_data = {
                    "municipality": muni_name,
                    "populationTotal": pop_total,
                    "populationSpanish": pop_spanish,
                    "populationForeign": pop_foreign,
                    "nationalityBreakdown": top_breakdown
                 }
                 self.wfile.write(json.dumps(response_data).encode('utf-8'))
                 return

            except Exception as e:
                print(f"DEBUG: API failed ({e}). Checking for mock data...")
                # Mock Data Fallback
                mock_db = {
                    "46078": { # Burjassot (Valencia)
                        "municipality": "Burjassot (Datos Oficiales 2024)",
                        "populationTotal": 40634,
                        "populationSpanish": 34040, # Approx based on 16.23% foreign
                        "populationForeign": 6594,
                        "nationalityBreakdown": [
                            {"name": "Colombia", "value": 1200}, # Estimated based on Valencia trends
                            {"name": "Rumanía", "value": 950},
                            {"name": "Italia", "value": 700},
                            {"name": "Venezuela", "value": 650},
                            {"name": "Marruecos", "value": 500},
                            {"name": "Ucrania", "value": 300},
                            {"name": "China", "value": 250},
                            {"name": "Argentina", "value": 200}
                        ]
                    },
                    "28079": { # Madrid
                        "populationTotal": 3332035,
                        "populationSpanish": 2849000,
                        "populationForeign": 483035,
                        "nationalityBreakdown": [
                            {"name": "Rumanía", "value": 45000},
                            {"name": "China", "value": 38000},
                            {"name": "Venezuela", "value": 35000},
                            {"name": "Colombia", "value": 32000}
                        ]
                    },
                    "08019": { # Barcelona
                         "populationTotal": 1660122,
                         "populationSpanish": 1300000,
                         "populationForeign": 360122,
                         "nationalityBreakdown": [
                             {"name": "Italia", "value": 40000},
                             {"name": "Pakistán", "value": 22000},
                             {"name": "China", "value": 20000}
                         ]
                    }
                    # Can add more later
                }
                
                if str(muni_id) in mock_db:
                    mock_data = mock_db[str(muni_id)]
                    mock_data["municipality"] = muni_name + " (Simulated Data)"
                    self.wfile.write(json.dumps(mock_data).encode('utf-8'))
                    return
                
                # If no mock data either
                self.wfile.write(json.dumps({"error": f"Data unavailable for {muni_name} (API Error & No Mock)"}).encode('utf-8'))


        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
