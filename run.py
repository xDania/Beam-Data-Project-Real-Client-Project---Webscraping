
import pandas as pd
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import boto3
import io
import subprocess

base_url = 'https://ressencewatches.com/pages/'
base_url_products = 'https://ressencewatches.com/collections/{}/products/{}'

# Function to extract image URL from meta tag
def extract_image_url(soup):
    meta_tag = soup.find('meta', property='og:image')
    return meta_tag['content'] if meta_tag else None

# Function to extract parent model
def extract_parent_model(type_url):
    # Split the URL by "/"
    parts = url.split("/")
    # Find the index of "collections"
    collection_index = parts.index("collections")
    # Get the next part after "collections"
    parent_model_with_hyphens = parts[collection_index + 1]
    # Remove hyphens and capitalize first letter of each word
    parent_model = parent_model_with_hyphens.replace("-", " ").title()
    return parent_model

type_urls = [
    'type-1-round',
    'type-1-squared',
    'type-2',
    'type-3',
    'type-5',
    'type-8',
]
products_urls = [
    'type-1-round-multicolour',
    'type-1-round-night-blue',
    'type-1-round-black',
    'type-1-squared-white',
    'type-1-squared-black',
    'type-1-squared-night-blue',
    'type-2-night-blue',
    'type-2-grey',
    'type-2-anthracite',
    'type-3-eucalyptus',
    'type-3-black',
    'type-3-white',
    'type-5-night-blue',
    'type-5-black-black',
    'type-8-cobalt-blue',
    'type-8-sage-green'
]
products_urls.append('type-8-cobalt-blue')

s3_bucket_name = 'rcp-input'
s3_file_key = 'output.csv'

all_product_info = []

for idx, type_url in enumerate(type_urls):
    start_index = idx * 3
    end_index = start_index + 3 if idx < 4 else start_index + 2  # Adjust for type 5 and type 8
    product_info_list = []

    for product_url in products_urls[start_index:end_index]:
        url = base_url_products.format(type_url, product_url)

        try:
            page = requests.get(url)
            page.raise_for_status()  # Check for HTTP errors
            soup = BeautifulSoup(page.content, 'html.parser')
            sections = soup.find_all(['strong', 'ul'])
            info_dict = {}
            section_title = None  # Initialize section_title here
            info_list = []  # Initialize info_list here
            for section in sections:
                if section.name == 'strong':
                    section_title = section.get_text()
                    info_list = []
                elif section.name == 'ul':
                    for li in section.find_all('li'):
                        info_list.append(li.get_text())
                    info_dict[section_title] = info_list

            # Extract product name
            product_name_element = soup.find('h1', class_='product-single__title')
            if product_name_element:
                product_name_text = product_name_element.text.strip()  # Extract text
                # parent_model = extract_parent_model(product_name_text, type_url)
                parent_model = extract_parent_model(type_url)

            else:
                product_name_text = "Not Found"
                parent_model = None

            # Extract image URL
            image_url = extract_image_url(soup)

            # Extract other product information from the product page
            price_element = soup.find('span', class_='product__price')
            if price_element:
                price_text = price_element.text.strip()
                currency, amount = price_text.split(' ', 1)  # Split on the first space
            else:
                amount = ""
                currency = ""

            # Extracting features from the dictionary info_dict
            functions = info_dict.get('FUNCTIONS', [])  # Get the list of functions or an empty list if not found
            features = '\n'.join(functions)  # Join the list of functions into a single string
            full_product_url = base_url_products.format(type_url, product_url)
            # Extracting jewels from the dictionary info_dict
            movement_info = info_dict.get('MOVEMENT', [])  # Get the list of movement info or an empty list if not found
            jewels = next((info for info in movement_info if 'jewels' in info), None)
            # Extracting power reserve from the dictionary info_dict
            power_reserve = next((info for info in movement_info if 'power reserve' in info), None)
            # Extract vibrations per hour
            vibrations = next((info for info in movement_info if 'vibrations per hour' in info), None)
            # Extract caliber
            caliber = '\n'.join(movement_info)
            # Extract movement
            movement = '\n'.join(movement_info)
            # Extract clasp_type
            # Check if 'BUCKLE & STRAP' key or 'BUCKLE & STRAP\xa0' key exists in info_dict
            if 'BUCKLE & STRAP' in info_dict:
                buckle_and_strap_info = info_dict['BUCKLE & STRAP']
            elif 'BUCKLE & STRAP\xa0' in info_dict:
                buckle_and_strap_info = info_dict['BUCKLE & STRAP\xa0']
            else:
                buckle_and_strap_info = []

            clasp_type = '\n'.join(buckle_and_strap_info[:2])
            bracelet_material = '\n'.join(buckle_and_strap_info[:2])
            dial_info = info_dict.get('DIAL', [])
            dial_color = ', '.join(dial_info)
            case_info = info_dict.get('CASE', [])
            water_resistance = next((info for info in case_info if 'resistance' in info), None)
            crystal = '\n'.join(case_info)
            case_thickness =  next((info for info in case_info if 'thickness' in info), None)
            between_lugs = '\n'.join(buckle_and_strap_info[:2])
            case_material =  '\n'.join(case_info)


            product_info = {
                'reference_number': product_name_text,
                'watch_URL': full_product_url,
                'type': ' ',
                'brand': 'Ressence',
                'year_introduced': ' ',
                'parent_model': parent_model,
                'specific_model': product_name_text,
                'nickname' : ' ',
                'marketing_name': ' ',
                'style': ' ',
                'currency': currency,
                'price': amount,
                'image_url': image_url,  # Add the image URL
                'made_in': 'Switzerland',
                'case_shape': ' ',
                'case_material' : case_material,
                'case_finish' :' ',
                'caseback'  : ' ',
                'diameter' : case_thickness,
                'between_lugs' : between_lugs,
                'lug_to_lug' : ' ',
                'case_thickness' : case_thickness,
                'bezel_material' : ' ',
                'bezel_color' : ' ',
                'crystal': crystal,
                'water_resistance':water_resistance,
                'weight':' ',
                'dial_color':dial_color,
                'numerals' :' ',
                'bracelet_material': bracelet_material,
                'bracelet_color': ' ',
                'clasp_type': clasp_type,
                'movement': movement,
                'caliber': caliber,
                'power_reserve': power_reserve,
                'frequency': vibrations,
                'jewels': jewels,
                'features': features,
                'description': ' ',
                'short_description': ' ',
            }

            product_info_list.append(product_info)

        except Exception as e:
            print(f"Error fetching data for {url}: {e}")

    all_product_info.extend(product_info_list)

# Write DataFrame to CSV
df = pd.DataFrame(all_product_info)
csv_buffer = io.StringIO()
df.to_csv(csv_buffer, index=False)
subprocess.run(['python3', 'upload_to_s3.py', csv_buffer.getvalue()])


print("CSV file created successfully.")