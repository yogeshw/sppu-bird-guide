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
    'Dicaeum erythrorhynchos': 'Dicaeum erythrorhynchos',  # Tickell's Flowerpecker - same
    'Sylvia curruca': 'Curruca curruca',  # Lesser Whitethroat - updated
    'Cacomantis passerinus': 'Cacomantis passerinus',  # Grey-bellied Cuckoo - same
    'Saxicola caprata': 'Saxicola caprata',  # Pied Bushchat - same
    'Hierococcyx varius': 'Hierococcyx varius',  # Common Hawk-Cuckoo - same
    'Strix ocellata': 'Strix ocellata',  # Mottled Wood Owl - same
    'Motacilla cinerea': 'Motacilla cinerea',  # Grey Wagtail - same
    'Motacilla alba': 'Motacilla alba',  # White Wagtail - same
    'Ardeola grayii': 'Ardeola grayii',  # Indian Pond Heron - same
    'Sturnia pagodarum': 'Sturnia pagodarum',  # Brahminy Starling - same
    'Aegithina tiphia': 'Aegithina tiphia',  # Common Iora - same
    'Cinnyris asiaticus': 'Cinnyris asiaticus',  # Purple Sunbird - same
    'Acridotheres fuscus': 'Acridotheres fuscus',  # Jungle Myna - same
    'Orthotomus sutorius': 'Orthotomus sutorius',  # Common Tailorbird - same
    'Merops orientalis': 'Merops orientalis',  # Asian Green Bee-eater - same
    'Parus cinereus': 'Parus cinereus',  # Asian Tit (Cinereous Tit) - same
    'Leptocoma zeylonica': 'Leptocoma zeylonica',  # Purple-rumped Sunbird - same
    'Rhipidura albogularis': 'Rhipidura albogularis',  # Spot-breasted Fantail - same
    'Falco peregrinus': 'Falco peregrinus',  # Peregrine Falcon - same
    'Cypsiurus balasiensis': 'Cypsiurus balasiensis',  # Asian Palm Swift - same
    'Dendrocitta vagabunda': 'Dendrocitta vagabunda',  # Rufous Treepie - same
    'Pseudibis papillosa': 'Pseudibis papillosa',  # Red-naped Ibis - same
    'Alcedo atthis': 'Alcedo atthis',  # Common Kingfisher - same
    'Motacilla maderaspatensis': 'Motacilla maderaspatensis',  # White-browed Wagtail - same
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
    'White-breasted Waterhen': ['White-breasted Water Hen', 'Common Waterhen'],
    'Lesser Whitethroat': ['Common Lesser Whitethroat', 'Siberian Lesser Whitethroat'],
    'Grey-bellied Cuckoo': ['Gray-bellied Cuckoo', 'Plaintive Cuckoo'],
    'Pied Bushchat': ['Common Pied Bushchat', 'African Pied Bushchat'],
    'Common Hawk-Cuckoo': ['Brainfever Bird', 'Brain-fever Bird'],
    'Mottled Wood Owl': ['Forest Spotted Owlet', 'Indian Wood Owl'],
    'Grey Wagtail': ['Gray Wagtail', 'Mountain Wagtail'],
    'White Wagtail': ['Pied Wagtail', 'European White Wagtail'],
    'Indian Pond Heron': ['Paddybird', 'Pond Heron'],
    'Brahminy Starling': ['Brahminy Myna', 'Pagoda Starling', 'Pagoda Myna'],
    'Common Iora': ['Marshall\'s Iora', 'Yellow-naped Iora'],
    'Purple Sunbird': ['Purple Honeysucker'],
    'Jungle Myna': ['Indian Jungle Myna', 'Dusky Myna'],
    'Common Tailorbird': ['Indian Tailorbird', 'Long-tailed Tailorbird'],
    'Asian Green Bee-eater': ['Little Green Bee-eater', 'Small Green Bee-eater'],
    'Asian Tit': ['Cinereous Tit', 'Grey Tit', 'Indian Grey Tit'],
    'Purple-rumped Sunbird': ['Ceylon Purple-rumped Sunbird'],
    'Spot-breasted Fantail': ['White-spotted Fantail', 'White-throated Fantail'],
    'Peregrine Falcon': ['Duck Hawk', 'Great Falcon'],
    'Asian Palm Swift': ['Palm Swift', 'Asian Palm-Swift'],
    'Rufous Treepie': ['Indian Treepie', 'Rufous Tree Pie'],
    'Red-naped Ibis': ['Indian Black Ibis', 'Black Ibis'],
    'Common Kingfisher': ['Eurasian Kingfisher', 'River Kingfisher'],
    'White-browed Wagtail': ['Large Pied Wagtail', 'Indian Pied Wagtail'],
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
    
    url = f"https://ebird.org/species/{species_code}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        matches = re.findall(r'https://cdn\.download\.ams\.birds\.cornell\.edu/api/v1/asset/(\d+)', response.text)
        print(matches)
        if matches:
            asset_id = matches[0]
            print(f"Found image asset: {asset_id}")
            
            details_url = f"https://search.macaulaylibrary.org/api/v1/asset/{asset_id}"
            details_response = requests.get(details_url)
            
            if details_response.status_code == 200:
                details = details_response.json()
                
                # Enhanced location formatting
                location = "Unknown location"
                if details.get('locationLine1') and details.get('locationLine2'):
                    location = f"{details['locationLine1']}, {details['locationLine2']}"
                elif details.get('locationLine1'):
                    location = details['locationLine1']
                elif details.get('locationLine2'):
                    location = details['locationLine2']
                
                # Enhanced photographer info
                photographer = details.get('userDisplayName', 'Unknown')
                if photographer != 'Unknown' and details.get('userId'):
                    photographer_url = f"https://ebird.org/profile/{details['userId']}"
                    photographer = f"{photographer} ({photographer_url})"

                return {
                    'url': f"https://cdn.download.ams.birds.cornell.edu/api/v1/asset/{asset_id}/2400",
                    'photographer': photographer,
                    'date': details.get('obsDt', '').split('T')[0],  # Format date without time
                    'location': location,
                    'catalog_id': asset_id,
                    'rights_holder': details.get('userDisplayName', ''),
                    'license': 'Macaulay Library © Cornell Lab of Ornithology'
                }
            else:
                # Fallback with basic info if details aren't available
                return {
                    'url': f"https://cdn.download.ams.birds.cornell.edu/api/v1/asset/{asset_id}/2400",
                    'photographer': 'Unknown',
                    'date': '',  # Ensure date field exists
                    'location': 'Unknown location',
                    'catalog_id': asset_id,
                    'rights_holder': '',  # Ensure rights_holder field exists
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
                        'date': '',  # Ensure date field exists
                        'location': 'Unknown location',
                        'catalog_id': asset_id,
                        'rights_holder': '',  # Ensure rights_holder field exists
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
                # Save enhanced credit information
                credit_filename = filename.replace('.jpg', '_credit.txt')
                credit_text = []
                
                # Add photographer with URL if available
                credit_text.append(credit_info.get('photographer', 'Unknown'))
                
                # Add location and date if available
                location_date = []
                if credit_info.get('location'):
                    location_date.append(credit_info['location'])
                if credit_info.get('date'):  # Use get() to safely check for date
                    location_date.append(credit_info['date'])
                if location_date:
                    credit_text.append(' - '.join(location_date))
                
                # Add attribution and license
                if credit_info.get('rights_holder'):  # Use get() to safely check
                    credit_text.append(f"© {credit_info['rights_holder']}")
                credit_text.append(credit_info.get('license', 'Macaulay Library © Cornell Lab of Ornithology'))
                credit_text.append(f"ML{credit_info['catalog_id']}")
                
                with open(credit_filename, 'w') as f:
                    f.write('\n'.join(credit_text))
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
    """Main function to download images and generate credit files"""
    # Set to True to regenerate credit files even if images exist
    download_credit = True
    
    workspace_root = Path(__file__).parent.parent
    api_key = getpass("Enter your eBird API key: ")
    
    images_dir = workspace_root / 'images'
    images_dir.mkdir(exist_ok=True)
    
    tex_file = workspace_root / 'latex' / 'bird_guide.tex'
    birds = extract_bird_info(tex_file)
    
    total_birds = len(birds)
    success_count = 0
    failed_birds = []
    
    for i, bird in enumerate(birds, 1):
        print(f"Processing {bird['common_name']} ({i}/{total_birds})...")
        
        image_filename = images_dir / f"{bird['common_name'].lower().replace(' ', '-')}.jpg"
        credit_filename = images_dir / f"{bird['common_name'].lower().replace(' ', '-')}_credit.txt"
        credit_needed = download_credit or not credit_filename.exists()
        
        if image_filename.exists() and not credit_needed:
            print(f"Image and credit exist for {bird['common_name']}, skipping.")
            success_count += 1
            continue
            
        # Get species code
        species_code = get_ebird_species_code(bird['common_name'], bird['latin_name'], api_key)
        if not species_code:
            print(f"Could not find species code for {bird['latin_name']}")
            failed_birds.append((bird['common_name'], "No species code found"))
            continue
        
        # Get best image info
        image_info = get_best_image(species_code, api_key)
        if not image_info:
            print(f"Could not find image info for {bird['common_name']}")
            failed_birds.append((bird['common_name'], "No image found"))
            continue
            
        if not image_filename.exists():
            # Need to download image and create credit
            if download_image(image_info['url'], str(image_filename), image_info):
                print(f"Successfully downloaded image and credit for {bird['common_name']}")
                success_count += 1
            else:
                print(f"Failed to download image for {bird['common_name']}")
                failed_birds.append((bird['common_name'], "Download failed"))
        elif credit_needed:
            # Only create credit file
            try:
                # Get fresh image info for credit update
                species_code = get_ebird_species_code(bird['common_name'], bird['latin_name'], api_key)
                if not species_code:
                    print(f"Could not find species code for credit update: {bird['common_name']}")
                    continue
                    
                image_info = get_best_image(species_code, api_key)
                if not image_info:
                    print(f"Could not find image info for credit update: {bird['common_name']}")
                    continue
                
                credit_text = []
                if image_info['photographer'] != 'Unknown':
                    credit_text.append(image_info['photographer'])
                
                location_date = []
                if image_info['location'] != 'Unknown location':
                    location_date.append(image_info['location'])
                if image_info['date']:
                    location_date.append(image_info['date'])
                if location_date:
                    credit_text.append(' - '.join(location_date))
                
                if image_info['rights_holder']:
                    credit_text.append(f"© {image_info['rights_holder']}")
                credit_text.append(image_info['license'])
                credit_text.append(f"ML{image_info['catalog_id']}")
                
                with open(credit_filename, 'w') as f:
                    f.write('\n'.join(filter(None, credit_text)))
                print(f"Successfully created credit file for {bird['common_name']}")
                success_count += 1
            except Exception as e:
                print(f"Error creating credit file: {e}")
                failed_birds.append((bird['common_name'], "Credit file creation failed"))

    # Special case for Cattle Egret handled similarly
    # ...rest of existing code...

if __name__ == "__main__":
    main()