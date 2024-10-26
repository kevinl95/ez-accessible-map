import folium
import pandas as pd
import re
import os
import requests

# Function to download the CSV file
def download_csv(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {filename} successfully.")
    else:
        print(f"Failed to download file: {response.status_code}")

# Function to parse "Georeference" column and extract latitude and longitude
def parse_georeference(point):
    if isinstance(point, str):
        match = re.search(r'POINT \((-?\d+\.\d+) (-?\d+\.\d+)\)', point)
        if match:
            lon, lat = float(match.group(1)), float(match.group(2))
            return lat, lon
    return None

def get_closest_place(lat, lon, api_key):
    places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius=1500&type=establishment&key={api_key}"
    response = requests.get(places_url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][1]['place_id']
    return None

# Function to get accessibility data from Google Places API
def get_accessibility_data(place_id, api_key):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        accessibility_info = data.get('result', {}).get('wheelchair_accessible_entrance', 'No accessibility information available')
        return accessibility_info
    else:
        return "Error retrieving data"

# Function to parse "Georeference" column and extract latitude and longitude
def parse_georeference(point):
    if isinstance(point, str):
        match = re.search(r'POINT \((-?\d+\.\d+) (-?\d+\.\d+)\)', point)
        if match:
            lon, lat = float(match.group(1)), float(match.group(2))
            return lat, lon
    return None

# URL of the CSV file
csv_url = "https://data.ny.gov/resource/y59h-w6v4.csv"
csv_filename = 'company_data.csv'

# Get the Google Places API key from environment variables
api_key = os.getenv('GOOGLE_PLACES_API_KEY')  # Use the environment variable
print(api_key)

# Download the CSV file
download_csv(csv_url, csv_filename)

# Load the CSV file into a DataFrame
df = pd.read_csv(csv_filename)

# Create a map centered on an average location
m = folium.Map(location=[41.106977, -73.547908], zoom_start=9)

# Loop through each row in the DataFrame and add markers to the map
for index, row in df.iterrows():
    georeference = row['georeference']
    company = row['company']
    location = parse_georeference(georeference)
    
    if location:
        lat, lon = location
        
        # Get the Place ID for the closest business
        closest_place_id = get_closest_place(lat, lon, api_key)
        if closest_place_id:
            accessibility_info = get_accessibility_data(closest_place_id, api_key)
            if "True" in accessibility_info:
                # Add marker to the map with a popup showing the company name and accessibility info
                folium.Marker(
                    location=location,
                    popup=f"<strong>{company}</strong><br>Wheelchair Accessible",
                    icon=folium.Icon(color='blue', icon='info-sign')
                ).add_to(m)
            else if "False" in accessibility_info:
                # Add marker to the map with a popup showing the company name and accessibility info
                folium.Marker(
                    location=location,
                    popup=f"<strong>{company}</strong><br>Not Wheelchair Accessible",
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(m)
            else:
                # Add marker to the map with a popup showing the company name and accessibility info
                folium.Marker(
                    location=location,
                    popup=f"<strong>{company}</strong><br>Accessibility Unknown",
                    icon=folium.Icon(color='yellow', icon='info-sign')
                ).add_to(m)

# Save the map as an HTML file
m.save('company_map.html')

print("Map created and saved as 'company_map.html'")