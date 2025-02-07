#!/usr/bin/env python3
import os
import re
import json
import requests
from getpass import getpass
from pathlib import Path
from difflib import get_close_matches
import time
import csv
from io import StringIO

# Known taxonomic updates - map old names to new eBird names
TAXONOMIC_UPDATES = {
    'Milvus migrans': 'Milvus migrans',  # Black Kite - same
    'Accipiter badius': 'Accipiter badius',  # Shikra - same
    'Amaurornis phoenicurus': 'Zapornia phoenicurus',  # White-breasted Waterhen - updated
    'Ardeola grayii': 'Ardeola grayii',  # Indian Pond Heron - same
    'Nycticorax nycticorax': 'Nycticorax nycticorax',  # Black-crowned Night Heron - same
    'Bubulcus ibis': 'Bubulcus ibis',  # Cattle Egret - same
    'Egretta garzetta': 'Egretta garzetta',  # Little Egret - same
    'Columba livia': 'Columba livia',  # Blue Rock Pigeon - same
    'Streptopelia chinensis': 'Spilopelia chinensis',  # Spotted Dove - updated
    'Streptopelia senegalensis': 'Spilopelia senegalensis',  # Little Brown Dove - updated
    'Vanellus indicus': 'Vanellus indicus',  # Red-wattled Lapwing - same
    'Eudynamys scolopacea': 'Eudynamys scolopaceus',  # Asian Koel - updated
    'Centropus sinensis': 'Centropus sinensis',  # Greater Coucal - same
    'Psittacula krameri': 'Psittacula krameri',  # Rose-ringed Parakeet - same
    'Psittacula eupatria': 'Alexandrinus eupatria',  # Alexandrine Parakeet - updated
    'Psittacula cyanocephala': 'Psittacula cyanocephala',  # Plum-headed Parakeet - same
    'Apus affinis': 'Apus affinis',  # House Swift - same
    'Halcyon smyrnensis': 'Halcyon smyrnensis',  # White-breasted Kingfisher - same
    'Megalaima haemacephala': 'Psilopogon haemacephalus',  # Coppersmith Barbet - updated
    'Hirundo concolor': 'Ptyonoprogne concolor',  # Dusky Crag Martin - updated
    'Hirundo rustica': 'Hirundo rustica',  # Barn Swallow - same
    'Hirundo daurica': 'Cecropis daurica',  # Red-rumped Swallow - updated
    'Hirundo smithii': 'Hirundo smithii',  # Wire-tailed Swallow - same
    'Lanius schach': 'Lanius schach',  # Long-tailed Shrike - same
    'Oriolus oriolus': 'Oriolus oriolus',  # Golden Oriole - same
    'Dicrurus macrocercus': 'Dicrurus macrocercus',  # Black Drongo - same
    'Dicrurus leucophaeus': 'Dicrurus leucophaeus',  # Ashy Drongo - same
    'Acridotheres tristis': 'Acridotheres tristis',  # Common Myna - same
    'Copsychus saularis': 'Copsychus saularis',  # Oriental Magpie-Robin - same
    'Pycnonotus cafer': 'Pycnonotus cafer',  # Red-vented Bulbul - same
    'Pycnonotus jocosus': 'Pycnonotus jocosus',  # Red-whiskered Bulbul - same
    'Turdoides malcolmi': 'Argya malcolmi',  # Large Grey Babbler - updated
    'Muscicapa tickelliae': 'Cyornis tickelliae',  # Tickell's Blue Flycatcher - updated
    'Prinia socialis': 'Prinia socialis',  # Ashy Prinia - same
    'Prinia sylvatica': 'Prinia sylvatica',  # Jungle Prinia - same
    'Passer domesticus': 'Passer domesticus',  # House Sparrow - same
    'Ploceus philippinus': 'Ploceus philippinus',  # Baya Weaver - same
    'Copsychus fulicatus': 'Saxicoloides fulicatus',  # Indian Robin - updated
    'Zosterops palpebrosus': 'Zosterops palpebrosus',  # Oriental White-eye - same
    'Lonchura punctulata': 'Lonchura punctulata',  # Scaly-breasted Munia - same
    'Corvus splendens': 'Corvus splendens',  # House Crow - same
    'Corvus macrorhynchos': 'Corvus macrorhynchos',  # Large-billed Crow - same
    'Athene brama': 'Athene brama',  # Spotted Owlet - same
    'Ocyceros birostris': 'Ocyceros birostris',  # Indian Grey Hornbill - same
    'Coracias benghalensis': 'Coracias benghalensis',  # Indian Roller - same
    'Coracina melanoptera': 'Coracina melanoptera',  # Black-headed Cuckoo-shrike - same
    'Pericrocotus cinnamomeus': 'Pericrocotus cinnamomeus',  # Small Minivet - same
    'Dicaeum erythrorhynchos': 'Dicaeum erythrorhynchos'  # Tickell's Flowerpecker - same
}

# Common name variants to help with matching
COMMON_NAME_VARIANTS = {
    'Blue Rock Pigeon': ['Rock Pigeon', 'Rock Dove', 'Common Pigeon'],
    'Little Brown Dove': ['Laughing Dove', 'Senegal Dove', 'Palm Dove'],
    'Asian Koel': ['Common Koel', 'Eastern Koel'],
    'White-breasted Kingfisher': ['White-throated Kingfisher', 'Smyrna Kingfisher'],
    'House Swift': ['Little Swift', 'Asian House Swift'],
    'Large Grey Babbler': ['Large Gray Babbler', "Malcolm's Babbler"],
    'Large-billed Crow': ['Jungle Crow', 'Large-billed Crow', 'Indian Jungle Crow'],
    'House Crow': ['Indian House Crow', 'Common House Crow'],
    'Indian Grey Hornbill': ['Indian Gray Hornbill', 'Common Grey Hornbill'],
    'Indian Roller': ['Blue Jay', 'Northern Roller', 'European Roller'],
    'Spotted Dove': ['Spilopelia chinensis', 'Pearl-necked Dove'],
    'Black Drongo': ['King Crow'],
    'Common Myna': ['Indian Myna', 'Common Mynah'],
    'Red-vented Bulbul': ['Common Bulbul'],
    'Oriental Magpie-Robin': ['Magpie Robin', 'Dyal Bird'],
    'House Sparrow': ['Indian Sparrow'],
    'Asian Koel': ['Koel', 'Common Koel'],
    'Greater Coucal': ['Crow Pheasant', 'Common Coucal'],
    'Red-wattled Lapwing': ['Did-he-do-it Bird'],
    'Rose-ringed Parakeet': ['Ring-necked Parakeet'],
    'Indian Robin': ['Black Robin', 'Indian Black Robin'],
    'Cattle Egret': ['Buff-backed Heron'],
    'Black Kite': ['Pariah Kite'],
    'Shikra': ['Little Banded Goshawk'],
    'White-breasted Waterhen': ['White-breasted Water Hen', 'Common Waterhen']
}

# Global cache for taxonomy data
TAXONOMY_CACHE = None

def fetch_taxonomy(api_key):
    """Fetch and cache the eBird taxonomy data"""
    global TAXONOMY_CACHE
    if (TAXONOMY_CACHE is not None):
        return TAXONOMY_CACHE
        
    url = "https://api.ebird.org/v2/ref/taxonomy/ebird"
    headers = {
        "X-eBirdApiToken": api_key
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        if (response.status_code == 200):
            TAXONOMY_CACHE = list(csv.DictReader(StringIO(response.text)))
            return TAXONOMY_CACHE
    except Exception as e:
        print(f"Error fetching taxonomy: {e}")
        return None

def extract_bird_info(tex_file):
    """Extract bird names and Latin names from the LaTeX file"""
    with open(tex_file, 'r') as f:
        content = f.read()
    
    # Find all birdentry commands
    pattern = r'\\birdentry{([^}]*)}{\\textit{([^}]*)}'
    matches = re.finditer(pattern, content)
    
    birds = []
    for match in matches:
        common_name = match.group(1)
        latin_name = match.group(2)
        # Update to current taxonomy if needed
        current_latin_name = TAXONOMIC_UPDATES.get(latin_name, latin_name)
        birds.append({
            'common_name': common_name,
            'latin_name': current_latin_name
        })
    return birds

def get_ebird_species_code(common_name, latin_name, api_key):
    """Get the eBird species code by searching through taxonomy CSV"""
    # Get taxonomy data from cache or fetch it
    taxonomy_data = fetch_taxonomy(api_key)
    if not taxonomy_data:
        print("Could not fetch taxonomy data")
        return None
        
    try:
        # First try scientific name match
        for row in taxonomy_data:
            # Check scientific name match
            if row['SCIENTIFIC_NAME'].lower() == latin_name.lower():
                print(f"Found match by scientific name: {row['SCIENTIFIC_NAME']}")
                return row['SPECIES_CODE']
        
        # If no scientific match, try common name
        for row in taxonomy_data:
            if row['COMMON_NAME'].lower() == common_name.lower():
                print(f"Found match by common name: {row['COMMON_NAME']}")
                return row['SPECIES_CODE']
        
        # Try variants if available
        if common_name in COMMON_NAME_VARIANTS:
            for variant in COMMON_NAME_VARIANTS[common_name]:
                for row in taxonomy_data:
                    if row['COMMON_NAME'].lower() == variant.lower():
                        print(f"Found match through variant: {variant}")
                        return row['SPECIES_CODE']
        
        # Try genus match as last resort
        genus = latin_name.split()[0]
        for row in taxonomy_data:
            if row['SCIENTIFIC_NAME'].lower().startswith(genus.lower()):
                print(f"Found genus match: {row['SCIENTIFIC_NAME']}")
                return row['SPECIES_CODE']
                
    except Exception as e:
        print(f"Error searching taxonomy: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"No match found for {common_name} ({latin_name})")
    return None

def get_best_image(species_code, api_key):
    """Get the best quality image for a species from eBird"""
    print(f"Getting image for {species_code}...")
    
    # Use ML's public web interface
    url = f"https://ebird.org/species/{species_code}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Get the species page
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Look for image URLs in the HTML
        matches = re.findall(r'https://cdn\.download\.ams\.birds\.cornell\.edu/api/v1/asset/(\d+)', response.text)
        if matches:
            asset_id = matches[0]  # Take the first image
            print(f"Found image asset: {asset_id}")
            
            # Try to get image details from ML
            details_url = f"https://search.macaulaylibrary.org/api/v1/asset/{asset_id}"
            details_response = requests.get(details_url)
            
            if details_response.status_code == 200:
                details = details_response.json()
                return {
                    'url': f"https://cdn.download.ams.birds.cornell.edu/api/v1/asset/{asset_id}/2400",
                    'photographer': details.get('userDisplayName', 'Unknown'),
                    'year': details.get('yearCreated', ''),
                    'location': details.get('locationLine2', 'Unknown location'),
                    'catalog_id': asset_id,
                    'license': 'Macaulay Library © Cornell Lab of Ornithology'
                }
            else:
                # Fallback with basic info if details aren't available
                return {
                    'url': f"https://cdn.download.ams.birds.cornell.edu/api/v1/asset/{asset_id}/2400",
                    'photographer': 'Unknown',
                    'year': '',
                    'location': 'Unknown location',
                    'catalog_id': asset_id,
                    'license': 'Macaulay Library © Cornell Lab of Ornithology'
                }
        else:
            print("No image found on species page")
            print("Trying catalog search...")
            
            # Try ML catalog search as fallback
            catalog_url = f"https://search.macaulaylibrary.org/catalog/search?taxonCode={species_code}&sort=rating_desc&mediaType=photo"
            response = requests.get(catalog_url, headers=headers)
            
            if response.status_code == 200:
                matches = re.findall(r'https://cdn\.download\.ams\.birds\.cornell\.edu/api/v1/asset/(\d+)', response.text)
                if matches:
                    asset_id = matches[0]
                    print(f"Found image through catalog: {asset_id}")
                    return {
                        'url': f"https://cdn.download.ams.birds.cornell.edu/api/v1/asset/{asset_id}/2400",
                        'photographer': 'Unknown',
                        'year': '',
                        'location': 'Unknown location',
                        'catalog_id': asset_id,
                        'license': 'Macaulay Library © Cornell Lab of Ornithology'
                    }
                    
    except Exception as e:
        print(f"Error getting image: {e}")
    
    return None

def download_image(url, filename, credit_info):
    """Download image and save credit information"""
    try:
        # Download image in chunks with progress
        print(f"Downloading from {url}")
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            
            # Get total size if available
            file_size = int(response.headers.get('content-length', 0))
            
            # Save image in chunks with progress
            downloaded = 0
            print("Saving image...")
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if file_size > 0:
                            percent = (downloaded / file_size) * 100
                            print(f"Progress: {percent:.1f}%", end='\r')
            
            print(f"\nDownloaded {downloaded} bytes")
            
            # Verify the file
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                # Save credit information
                credit_filename = filename.replace('.jpg', '_credit.txt')
                credit_text = (
                    f"{credit_info['photographer']} - {credit_info['location']}\n"
                    f"{credit_info['license']}\n"
                    f"ML{credit_info['catalog_id']}"
                )
                with open(credit_filename, 'w') as f:
                    f.write(credit_text)
                return True
            else:
                print("Error: Downloaded file is empty or missing")
                if os.path.exists(filename):
                    os.remove(filename)
                return False
                
    except Exception as e:
        print(f"Error downloading image: {e}")
        if os.path.exists(filename):
            os.remove(filename)
        return False

def main():
    # Get the workspace root directory
    workspace_root = Path(__file__).parent.parent
    
    # Get eBird API key
    api_key = getpass("Enter your eBird API key: ")
    
    # Create images directory if it doesn't exist
    images_dir = workspace_root / 'images'
    images_dir.mkdir(exist_ok=True)
    
    # Extract bird information from LaTeX file
    tex_file = workspace_root / 'latex' / 'bird_guide.tex'
    birds = extract_bird_info(tex_file)
    
    # Track progress
    total_birds = len(birds)
    success_count = 0
    failed_birds = []
    
    # Process each bird
    for i, bird in enumerate(birds, 1):
        print(f"Processing {bird['common_name']} ({i}/{total_birds})...")
        
        # Check if image already exists
        image_filename = images_dir / f"{bird['common_name'].lower().replace(' ', '-')}.jpg"
        if image_filename.exists():
            print(f"Image already exists for {bird['common_name']}, skipping download.")
            success_count += 1
            continue
        
        # Get species code
        species_code = get_ebird_species_code(bird['common_name'], bird['latin_name'], api_key)
        if not species_code:
            print(f"Could not find species code for {bird['latin_name']}")
            failed_birds.append((bird['common_name'], "No species code found"))
            continue
        
        # Get best image
        image_info = get_best_image(species_code, api_key)
        if not image_info:
            print(f"Could not find image for {bird['common_name']}")
            failed_birds.append((bird['common_name'], "No image found"))
            continue
        
        # Download image and save credit info
        if download_image(image_info['url'], str(image_filename), image_info):
            print(f"Successfully downloaded image for {bird['common_name']}")
            success_count += 1
        else:
            print(f"Failed to download image for {bird['common_name']}")
            failed_birds.append((bird['common_name'], "Download failed"))
    
    # Special case for Cattle Egret
    cattle_egret_filename = images_dir / "cattle-egret.jpg"
    if not cattle_egret_filename.exists():
        print("Processing Cattle Egret...")
        species_code = "categr2"
        image_info = get_best_image(species_code, api_key)
        if image_info:
            if download_image(image_info['url'], str(cattle_egret_filename), image_info):
                print("Successfully downloaded image for Cattle Egret")
                success_count += 1
            else:
                print("Failed to download image for Cattle Egret")
                failed_birds.append(("Cattle Egret", "Download failed"))
        else:
            print("Could not find image for Cattle Egret")
            failed_birds.append(("Cattle Egret", "No image found"))
    else:
        print("Image already exists for Cattle Egret, skipping download.")
        success_count += 1
    
    # Print summary
    print("\nDownload Summary:")
    print(f"Successfully downloaded: {success_count}/{total_birds + 1} images")
    if failed_birds:
        print("\nFailed to process the following birds:")
        for bird, reason in failed_birds:
            print(f"- {bird}: {reason}")

if __name__ == "__main__":
    main()