# utils/api_handler.py
import requests
import os
import re
from pathlib import Path

def fetch_all_products():
    """
    Fetches all products from DummyJSON API
    Returns: list of product dictionaries
    """
    try:
        url = "https://dummyjson.com/products?limit=100"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        products = data['products']
        
        # Filter to required fields only
        return [
            {
                'id': product['id'],
                'title': product['title'],
                'category': product['category'],
                'brand': product['brand'],
                'price': product['price'],
                'rating': product['rating']
            }
            for product in products
        ]
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return []
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []


def create_product_mapping(api_products):
    """
    Creates a mapping of product IDs to product info
    Returns: dictionary mapping product IDs to info
    """
    mapping = {}
    for product in api_products:
        mapping[product['id']] = {
            'title': product['title'],
            'category': product['category'],
            'brand': product['brand'],
            'rating': product['rating']
        }
    return mapping


def extract_product_id(product_id_str):
    """
    Extract numeric ID from ProductID like P101 -> 101, P5 -> 5
    """
    match = re.search(r'P(\d+)', product_id_str)
    return int(match.group(1)) if match else None


def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transaction data with API product information
    Returns: list of enriched transaction dictionaries
    """
    enriched_transactions = []
    
    for trans in transactions:
        enriched = trans.copy()
        product_id_str = trans['ProductID']
        
        # Extract numeric ID from ProductID
        api_id = extract_product_id(product_id_str)
        
        if api_id and api_id in product_mapping:
            api_product = product_mapping[api_id]
            enriched.update({
                'API_Category': api_product['category'],
                'API_Brand': api_product['brand'],
                'API_Rating': api_product['rating'],
                'API_Match': True
            })
        else:
            # No match found
            enriched.update({
                'API_Category': None,
                'API_Brand': None,
                'API_Rating': None,
                'API_Match': False
            })
        
        enriched_transactions.append(enriched)
    
    # Save to file
    save_enriched_data(enriched_transactions)
    
    return enriched_transactions


def save_enriched_data(enriched_transactions, filename='data/enriched_sales_data.txt'):
    """
    Saves enriched transactions back to pipe-delimited file
    """
    # Create data directory if it doesn't exist
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    
    # Header with new columns
    header = [
        'TransactionID', 'Date', 'ProductID', 'ProductName', 'Quantity', 
        'UnitPrice', 'CustomerID', 'Region', 'API_Category', 
        'API_Brand', 'API_Rating', 'API_Match'
    ]
    
    with open(filename, 'w') as f:
        # Write header
        f.write('|'.join(header) + '\n')
        
        # Write data rows
        for trans in enriched_transactions:
            row = [
                str(trans.get('TransactionID', '')),
                str(trans.get('Date', '')),
                str(trans.get('ProductID', '')),
                str(trans.get('ProductName', '')),
                str(trans.get('Quantity', 0)),
                str(trans.get('UnitPrice', 0.0)),
                str(trans.get('CustomerID', '')),
                str(trans.get('Region', '')),
                str(trans.get('API_Category', '')) or '',
                str(trans.get('API_Brand', '')) or '',
                str(trans.get('API_Rating', '')) or '',
                str(trans.get('API_Match', False))
            ]
            f.write('|'.join(row) + '\n')
    
    print(f"Enriched data saved to: {filename}")


# Test code (runs only when executed directly)
if __name__ == "__main__":
    """Complete Part 3 pipeline test"""
    try:
        from file_handler import read_sales_data, parse_transactions, validate_and_filter
        from data_processor import calculate_total_revenue
        
        print("=== PART 3: API Integration Test ===")
        
        # Step 1: Get API products
        print("1. Fetching products from API...")
        api_products = fetch_all_products()
        print(f"✓ Fetched {len(api_products)} products")
        
        # Step 2: Create mapping
        product_mapping = create_product_mapping(api_products)
        print(f"✓ Created mapping for {len(product_mapping)} product IDs")
        
        # Step 3: Load and process sales data
        raw_lines = read_sales_data('sales_data.txt')
        transactions = parse_transactions(raw_lines)
        valid_trans, _, _ = validate_and_filter(transactions)
        print(f"✓ Loaded {len(valid_trans)} valid transactions")
        
        # Step 4: Enrich data
        enriched = enrich_sales_data(valid_trans, product_mapping)
        matches = sum(1 for t in enriched if t['API_Match'])
        print(f"✓ Enriched {len(enriched)} transactions ({matches} API matches)")
        
        # Stats
        print(f"Sample enriched transaction: {list(enriched[0].items())[:6]}")
        
    except ImportError as e:
        print(f"Missing Part 1/2 files: {e}")
        print("Install requests: pip install requests")
    except Exception as e:
        print(f"Test failed: {e}")