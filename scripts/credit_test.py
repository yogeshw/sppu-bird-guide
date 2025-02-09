#!/usr/bin/env python3

import requests
from getpass import getpass
from bs4 import BeautifulSoup
from download_ebird_images import get_ebird_species_code

def get_best_image_debug(species_code, api_key):
    """Debug version of get_best_image that scrapes Macaulay Library webpage"""
    print(f"Getting image for {species_code}...")
    
    try:
        # Try direct asset page first since we know the species code
        asset_url = f"https://ebird.org/species/{species_code}"
        print(f"\nFetching species page: {asset_url}")
        
        response = requests.get(asset_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print("\nLooking for main species image...")
        
        # First try to find the main species image container
        media_link = None
        for selector in [
            '.SpeciesHeader img[src*="cdn.download.ams.birds.cornell.edu"]',  # Main header image
            '.MediaFeed-main img',  # Main media feed image
            'img[src*="ML25502811"]'  # Specific asset ID for this species
        ]:
            img = soup.select_one(selector)
            if img:
                print(f"Found main image using selector: {selector}")
                # Extract asset ID from src URL
                src = img.get('src', '')
                if '/asset/' in src:
                    asset_id = src.split('/asset/')[-1].split('/')[0]
                    media_link = True  # Just need a truthy value
                    break
        
        if not media_link:
            print("Could not find main species image, trying fallback methods...")
            # Print available image sources for debugging
            print("Available images:", [img['src'] for img in soup.find_all('img', src=True)])
            # Fallback to known asset ID for this species
            asset_id = "25502811"
            
        print(f"Using asset ID: {asset_id}")
        
        # Get asset page
        asset_url = f"https://macaulaylibrary.org/asset/{asset_id}"
        print(f"\nFetching asset page: {asset_url}")
        
        response = requests.get(asset_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try multiple selectors for photographer info with more specific selectors
        photographer = None
        for selector in [
            'div.MediaInfo span.MediaInfo-photographer',  # Most specific
            'span.MediaInfo-photographer',
            '.AssetInfo span[class*="photographer"]',
            '.Photo-credit',
            '.Asset-credit'
        ]:
            elem = soup.select_one(selector)
            if elem:
                photographer = elem.text.strip()
                print(f"Found photographer using selector: {selector}")
                break
                
        if not photographer:
            print("\nCould not find photographer, dumping relevant HTML sections:")
            for section in soup.select('.MediaInfo, .AssetInfo, .Photo-credit'):
                print("\nSection HTML:")
                print(section.prettify())
            photographer = 'Unknown'
        
        # Rest of the function remains same
        location_elem = soup.find('div', class_='MediaInfo-location')
        date_elem = soup.find('div', class_='MediaInfo-date')
        
        return {
            'url': f"https://cdn.download.ams.birds.cornell.edu/api/v2/asset/{asset_id}/2400",
            'photographer': photographer,
            'date': date_elem.text.strip() if date_elem else '',
            'location': location_elem.text.strip() if location_elem else 'Unknown location',
            'catalog_id': asset_id,
            'rights_holder': photographer,
            'license': 'Macaulay Library at the Cornell Lab of Ornithology'
        }
    
    except requests.exceptions.RequestException as e:
        print(f"Network error in get_best_image_debug: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"Error in get_best_image_debug: {e}")
        import traceback
        traceback.print_exc()
    
    return None

def format_credit(image_info):
    """Format credit line in standard format"""
    if not image_info:
        return "No image information available"
    
    # Extract photographer name (remove URL if present)
    photographer = image_info['photographer']
    if '(' in photographer:
        photographer = photographer.split('(')[0].strip()
    
    return f"{photographer} / Macaulay Library at the Cornell Lab of Ornithology (ML{image_info['catalog_id']})"

def main():
    api_key = getpass("Enter your eBird API key: ")
    
    test_bird = {
        'common_name': 'Black Kite',
        'latin_name': 'Milvus migrans'
    }
    
    species_code = get_ebird_species_code(test_bird['common_name'], test_bird['latin_name'], api_key)
    if not species_code:
        print(f"Could not find species code for {test_bird['common_name']}")
        return
    
    # Use debug version instead
    image_info = get_best_image_debug(species_code, api_key)
    if not image_info:
        print(f"Could not find image info for {test_bird['common_name']}")
        return
    
    print("\nFinal image_info dictionary:")
    for key, value in image_info.items():
        print(f"{key}: {value}")
    
    credit_line = format_credit(image_info)
    print("\nFormatted credit line:")
    print(credit_line)

if __name__ == "__main__":
    main()
