import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.ine_client import ine_client

def test_search_and_fetch():
    muni_query = "Madrid"
    print(f"Searching for '{muni_query}'...")
    matches = ine_client.search_municipality(muni_query)
    
    if not matches:
        print("No matches found.")
        return

    print(f"Found {len(matches)} matches. Top match: {matches[0]['Nombre']} (ID: {matches[0]['Id']})")
    
    selected_muni = matches[0]
    muni_id = selected_muni["Id"]
    
    print(f"Fetching data for Municipality ID: {muni_id}...")
    
    # Simulate logic from demographics.py
    # We fetch data filtering by this municipality
    
    # We need to construct the params carefully.
    # The API might return too much data if we don't filter by Sex and Nationality too.
    # But filtering by Municipality (96193) should restrict it to that geo at least.
    
    data_rows = ine_client.get_data("33784", {"tv": f"96193:{muni_id}", "date": "20230101"}) # Try 2023 or remove date
    
    if not data_rows:
        print("No data rows returned. Trying without date...")
        data_rows = ine_client.get_data("33784", {"tv": f"96193:{muni_id}"})
    
    print(f"Received {len(data_rows)} data rows.")
    
    # Print sample rows to understand structure
    for i, row in enumerate(data_rows[:5]):
        print(f"Row {i}: {row['Nombre']} - Value: {row['Data'][0]['Valor'] if row['Data'] else 'No Data'}")

if __name__ == "__main__":
    test_search_and_fetch()
