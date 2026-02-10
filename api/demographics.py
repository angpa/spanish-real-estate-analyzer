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
            # Table 33784: Population by sex, municipalities and nationality
            # We need to constructing the "codes" for the query.
            # Usually: TV=VarID:ValueID
            # Sexo (96192): Total (let's assume ID is known or we fetch all)
            # Nacionalidad (96194): We want breakdown.
            
            # For simplicity in this V1, let's fetch data specifically for this municipality.
            # We can use the 'date' parameter to get the latest.
            
            # Fetching variable values for Sexo to find "Total"
            sexos = ine_client.get_variable_values("33784", "96192")
            total_sex_id = next((s["Id"] for s in sexos if "Total" in s["Nombre"]), None)
            
            # Fetching variable values for Nacionalidad
            nacionalidades = ine_client.get_variable_values("33784", "96194")
            total_nat_id = next((n["Id"] for n in nacionalidades if "Total" in n["Nombre"]), None)
            spaniards_id = next((n["Id"] for n in nacionalidades if "Española" in n["Nombre"]), None)
            foreigners_id = next((n["Id"] for n in nacionalidades if "Extranjera" in n["Nombre"]), None)

            # Construct params
            # We filter by Municipality ID
            # tv = VariableID:ValueID
            # We want all rows where Municipality is the selected one
            
            # NOTE: INE API can be tricky with filters. 
            # A safer way often is to get the table data filtered by the specific municipality value.
            # 96193 is Municipality Variable ID.
            
            req_params = {
                "tv": f"96193:{muni_id}", # Filter by this municipality
                "date": "20230101", # Try to get latest data (need to verify usually)
                # "per": "12" # Annual often
            }
            
            # If we don't specify date, it might return all series. Let's try requesting without date first to see series,
            # or better validation: fetch latest n=1
            
            # Let's request the table data for this municipality
            data_rows = ine_client.get_data("33784", {"tv": f"96193:{muni_id}"})
            
            # Process Data
            # We look for:
            # - Sexo: Total
            # - Nacionalidad: Total, Española, Extranjera
            
            pop_total = 0
            pop_spanish = 0
            pop_foreign = 0
            breakdown = []

            for row in data_rows:
                # Check Metadata for this row
                # We need to parse which variable values this row corresponds to.
                # The API returns "FK_Unidad", "FK_Escala", "Calculo", "Data" list
                # But filtering by "tv" usually returns the series. 
                # The "Nombre" field in the series descriptor usually contains the concatenation of values.
                
                # A more robust way is to inspect "Data" and "Nombre".
                # "Nombre" ex: "Total. Madrid. Total. " (Sex. Muni. Nationality)
                
                name = row.get("Nombre", "")
                
                # Filter for "Total" sex only
                if "Total" not in name.split(".")[0]: # Assuming Sex is first? Need verification.
                     # Actually, order depends on variable definition order usually.
                     # Let's use simple string matching for V1 or fetch variable IDs if strict.
                     pass
                
                latest_value = 0
                if row.get("Data"):
                    # Sort by date descending
                    sorted_data = sorted(row["Data"], key=lambda x: x.get("Fecha", 0), reverse=True)
                    if sorted_data:
                        latest_value = sorted_data[0].get("Valor", 0)

                # Identify which metric this is
                if "Española" in name and "Total" in name.split(".")[0]:
                     pop_spanish = latest_value
                elif "Extranjera" in name and "Total" in name.split(".")[0]:
                     pop_foreign = latest_value
                elif "Total" in name and "Total" in name.split(".")[0] and "Española" not in name and "Extranjera" not in name:
                     # This might be the Grand Total, but "Total" appears twice (Sex Total, Nat Total)
                     # Usually formatted "Sex. Muni. Nat."
                     # "Total. Madrid. Total." -> Grand Total
                     pop_total = latest_value
                
                # Detailed breakdown
                if "Total" in name.split(".")[0] and "Española" not in name and "Extranjera" not in name and "Total" not in name.split(".")[-2]: # Rough heuristic
                     # Likely a specific nationality
                     # Clean name
                     nat_name = name.split(".")[-2].strip() # Assuming last part is empty space/dot
                     if nat_name and nat_name != "Total" and latest_value > 0:
                         breakdown.append({"name": nat_name, "value": latest_value})

            # Sort breakdown
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

        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
