def read_sales_data(filename):
    """
    Reads sales data from file handling encoding issues
    Returns: list of raw lines (strings)
    Expected Output Format:
    ['T001|2024-12-01|P101|Laptop|2|45000|C001|North', ...]
    """
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as file:
                lines = file.readlines()
                # Skip header row and remove empty lines
                raw_lines = [line.strip() for line in lines[1:] if line.strip()]
                return raw_lines
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: File '{filename}' not found.")
        except UnicodeDecodeError:
            continue
    
    raise FileNotFoundError(f"Error: Could not read file '{filename}' with any supported encoding.")


def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries
    Returns: list of dictionaries with keys:
    ['TransactionID', 'Date', 'ProductID', 'ProductName', 'Quantity', 'UnitPrice', 'CustomerID', 'Region']
    """
    transactions = []
    
    for line in raw_lines:
        try:
            fields = line.split('|')
            
            # Skip rows with incorrect number of fields
            if len(fields) != 8:
                continue
            
            # Handle commas within ProductName and UnitPrice
            product_name = fields[3].replace(',', ' ').strip()
            unit_price_str = fields[5].replace(',', '').strip()
            
            transaction = {
                'TransactionID': fields[0].strip(),
                'Date': fields[1].strip(),
                'ProductID': fields[2].strip(),
                'ProductName': product_name,
                'Quantity': int(fields[4].strip()),
                'UnitPrice': float(unit_price_str),
                'CustomerID': fields[6].strip(),
                'Region': fields[7].strip()
            }
            transactions.append(transaction)
        except (ValueError, IndexError):
            continue
    
    return transactions


def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters
    Returns: tuple (valid_transactions, invalid_count, filter_summary)
    """
    valid_transactions = []
    invalid_count = 0
    transaction_amounts = []
    
    # Validate transactions
    for trans in transactions:
        is_valid = True
        
        # Validation rules
        if trans['Quantity'] <= 0 or trans['UnitPrice'] <= 0:
            is_valid = False
        if not trans['TransactionID'].startswith('T'):
            is_valid = False
        if not trans['ProductID'].startswith('P'):
            is_valid = False
        if not trans['CustomerID'].startswith('C'):
            is_valid = False
        
        if is_valid:
            amount = trans['Quantity'] * trans['UnitPrice']
            transaction_amounts.append(amount)
            valid_transactions.append(trans)
        else:
            invalid_count += 1
    
    # Print available regions
    regions = set(t['Region'] for t in valid_transactions)
    print(f"Available regions: {sorted(regions)}")
    
    # Print amount range
    if transaction_amounts:
        print(f"Transaction amount range: {min(transaction_amounts):.2f} - {max(transaction_amounts):.2f}")
    
    # Apply region filter
    filtered_by_region = 0
    if region:
        original_count = len(valid_transactions)
        valid_transactions = [t for t in valid_transactions if t['Region'] == region]
        filtered_by_region = original_count - len(valid_transactions)
        print(f"Records after region filter ({region}): {len(valid_transactions)}")
    
    # Apply amount filter
    filtered_by_amount = 0
    if min_amount or max_amount:
        original_count = len(valid_transactions)
        valid_transactions = [
            t for t in valid_transactions
            if (min_amount is None or t['Quantity'] * t['UnitPrice'] >= min_amount) and
               (max_amount is None or t['Quantity'] * t['UnitPrice'] <= max_amount)
        ]
        filtered_by_amount = original_count - len(valid_transactions)
        print(f"Records after amount filter: {len(valid_transactions)}")
    
    # Filter summary
    filter_summary = {
        'total_input': len(transactions),
        'invalid': invalid_count,
        'filtered_by_region': filtered_by_region,
        'filtered_by_amount': filtered_by_amount,
        'final_count': len(valid_transactions)
    }
    
    return valid_transactions, invalid_count, filter_summary


# Test code (runs only when file executed directly)
if __name__ == "__main__":
    print("Testing Part 1 functions...")
    raw_lines = read_sales_data('sales_data.txt')
    print(f"✓ Read {len(raw_lines)} raw lines")
    
    transactions = parse_transactions(raw_lines)
    print(f"✓ Parsed {len(transactions)} transactions")
    
    valid, invalid, summary = validate_and_filter(transactions)
    print(f"✓ Summary: {summary}")