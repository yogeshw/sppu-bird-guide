#!/usr/bin/env python3
import requests
from getpass import getpass
import csv
from io import StringIO
from pathlib import Path
import os
import re

def get_species_code(api_key, species="Shikra", scientific_name="Accipiter badius"):
    """Test getting species code using eBird's taxonomy API"""
    print(f"Looking up code for {species} ({scientific_name})")
    
    # Use the JSON format of taxonomy
    url = "https://api.ebird.org/v2/ref/taxonomy/ebird?fmt=json"
    headers = {
        "X-eBirdApiToken": api_key
    }
    
    try:
        print("\nQuerying eBird taxonomy...")
        response = requests.get(url, headers=headers)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            species_list = response.json()
            print(f"Retrieved {len(species_list)} species entries")
            
            # Try exact matches first
            for entry in species_list:
                if entry['sciName'].lower() == scientific_name.lower() or entry['comName'].lower() == species.lower():
                    print(f"\nFound match:")
                    print(f"Code: {entry['speciesCode']}")
                    print(f"Scientific name: {entry['sciName']}")
                    print(f"Common name: {entry['comName']}")
                    return entry['speciesCode']
            
            print("\n✗ No exact match found")
            return None
            
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return None

def get_best_image(api_key, species_code):
    """Test getting the best image for a species"""
    print(f"\nTrying to get image for species code: {species_code}")
    
    # Use ML's public web interface
    url = f"https://ebird.org/species/{species_code}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("Getting species page...")
        response = requests.get(url, headers=headers)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Look for the main image URL in the HTML
            matches = re.findall(r'https://cdn\.download\.ams\.birds\.cornell\.edu/api/v1/asset/(\d+)', response.text)
            if matches:
                asset_id = matches[0]  # Take the first image
                print(f"Found asset ID: {asset_id}")
                
                # Get the image details from ML
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
                print("\nTrying ML catalog search...")
                
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
        print(f"\n✗ Error getting image: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return None

def download_image(url, filename, credit_info):
    """Download the image and save credit information"""
    print(f"\nDownloading image to: {filename}")
    
    try:
        # Download image in chunks with progress
        print(f"Requesting URL: {url}")
        with requests.get(url, stream=True) as response:
            print(f"Response status: {response.status_code}")
            print(f"Content type: {response.headers.get('content-type', 'unknown')}")
            print(f"Content length: {response.headers.get('content-length', 'unknown')} bytes")
            
            response.raise_for_status()
            
            # Save image in chunks with progress
            file_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            downloaded = 0
            
            print("\nSaving image...")
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if file_size > 0:
                            percent = (downloaded / file_size) * 100
                            print(f"Progress: {percent:.1f}% ({downloaded}/{file_size} bytes)", end='\r')
            
            if file_size > 0:
                print(f"\nDownloaded: {downloaded}/{file_size} bytes ({(downloaded/file_size)*100:.1f}%)")
            else:
                print(f"\nDownloaded: {downloaded} bytes")
        
        # Verify the downloaded file
        if not os.path.exists(filename):
            print("✗ Error: File was not created")
            return False
            
        file_size = os.path.getsize(filename)
        if file_size == 0:
            print("✗ Error: Downloaded file is empty")
            return False
            
        print(f"Final file size: {file_size} bytes")
        
        # Save credit information
        credit_filename = filename.replace('.jpg', '_credit.txt')
        credit_text = (
            f"{credit_info['photographer']} - {credit_info['location']}\n"
            f"{credit_info['license']}\n"
            f"ML{credit_info['catalog_id']}"
        )
        with open(credit_filename, 'w') as f:
            f.write(credit_text)
            
        print("✓ Successfully saved image and credit info")
        return True
        
    except Exception as e:
        print(f"\n✗ Error downloading image: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Try to clean up partial downloads
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print("Cleaned up partial download")
            except:
                pass
        return False

def main():
    print("=" * 60)
    print("eBird Species Code and Image Download Test")
    print("Target: Shikra (Accipiter badius)")
    print("Expected code: shikra1")
    print("=" * 60)
    
    api_key = getpass("\nEnter your eBird API key: ")
    print("\nStarting lookup...")
    
    # Get species code
    code = get_species_code(api_key)
    
    if code:
        print(f"\nFound species code: {code}")
        if code == 'shikra1':
            print("✓ Code validation passed")
            
            # Try to get image
            image_info = get_best_image(api_key, code)
            if image_info:
                print("\nFound image, attempting download...")
                
                # Create images directory if it doesn't exist
                images_dir = Path(__file__).parent.parent / 'images'
                images_dir.mkdir(exist_ok=True)
                
                # Download image
                image_filename = images_dir / "shikra.jpg"
                if download_image(image_info['url'], str(image_filename), image_info):
                    print("\n✓ Successfully downloaded image")
                else:
                    print("\n✗ Failed to download image")
            else:
                print("\n✗ Could not find suitable image")
        else:
            print("\n✗ Retrieved incorrect species code")
    else:
        print("\n✗ Could not find species code")
        print("\nTroubleshooting tips:")
        print("1. Check your API key at https://ebird.org/api/keygen")
        print("2. Try searching for Shikra at https://ebird.org/species")
        print("3. Try accessing https://api.ebird.org/v2/ref/taxonomy/ebird directly")
    print("=" * 60)

if __name__ == "__main__":
    main()