# utils/data_processor.py

def calculate_total_revenue(transactions):
    """Calculates total revenue from all transactions. Returns: float"""
    total = 0.0
    for trans in transactions:
        total += trans['Quantity'] * trans['UnitPrice']
    return total


def region_wise_sales(transactions):
    """
    Calculate total sales per region with transaction count and percentage
    Returns dict sorted by total_sales descending
    """
    region_stats = {}
    total_revenue = calculate_total_revenue(transactions)
    
    for trans in transactions:
        region = trans['Region']
        amount = trans['Quantity'] * trans['UnitPrice']
        
        if region not in region_stats:
            region_stats[region] = {'total_sales': 0.0, 'transaction_count': 0}
        region_stats[region]['total_sales'] += amount
        region_stats[region]['transaction_count'] += 1
    
    # Add percentages
    for region in region_stats:
        region_stats[region]['percentage'] = round(
            (region_stats[region]['total_sales'] / total_revenue) * 100, 2
        )
    
    return dict(sorted(region_stats.items(), key=lambda x: x[1]['total_sales'], reverse=True))


def top_selling_products(transactions, n=5):
    """Returns top n products: (ProductName, TotalQuantity, TotalRevenue)"""
    product_stats = {}
    
    for trans in transactions:
        product = trans['ProductName']
        qty = trans['Quantity']
        revenue = qty * trans['UnitPrice']
        
        if product not in product_stats:
            product_stats[product] = {'total_qty': 0, 'total_revenue': 0.0}
        product_stats[product]['total_qty'] += qty
        product_stats[product]['total_revenue'] += revenue
    
    product_list = [
        (name, stats['total_qty'], round(stats['total_revenue'], 2))
        for name, stats in product_stats.items()
    ]
    product_list.sort(key=lambda x: x[1], reverse=True)
    return product_list[:n]


def customer_analysis(transactions):
    """Customer analysis: total_spent, purchase_count, avg_order_value, products_bought"""
    customer_stats = {}
    
    for trans in transactions:
        customer = trans['CustomerID']
        amount = trans['Quantity'] * trans['UnitPrice']
        product = trans['ProductName']
        
        if customer not in customer_stats:
            customer_stats[customer] = {
                'total_spent': 0.0,
                'purchase_count': 0,
                'products_bought': set()
            }
        customer_stats[customer]['total_spent'] += amount
        customer_stats[customer]['purchase_count'] += 1
        customer_stats[customer]['products_bought'].add(product)
    
    # Calculate metrics and sort
    for customer in customer_stats:
        stats = customer_stats[customer]
        stats['avg_order_value'] = round(stats['total_spent'] / stats['purchase_count'], 2)
        stats['products_bought'] = sorted(list(stats['products_bought']))
    
    return dict(sorted(customer_stats.items(), key=lambda x: x[1]['total_spent'], reverse=True))


def daily_sales_trend(transactions):
    """Daily sales with revenue, transaction_count, unique_customers - chronological"""
    daily_stats = {}
    
    for trans in transactions:
        date = trans['Date']
        customer = trans['CustomerID']
        amount = trans['Quantity'] * trans['UnitPrice']
        
        if date not in daily_stats:
            daily_stats[date] = {'revenue': 0.0, 'transaction_count': 0, 'unique_customers': set()}
        daily_stats[date]['revenue'] += amount
        daily_stats[date]['transaction_count'] += 1
        daily_stats[date]['unique_customers'].add(customer)
    
    for date in daily_stats:
        daily_stats[date]['unique_customers'] = len(daily_stats[date]['unique_customers'])
    
    return dict(sorted(daily_stats.items()))


def find_peak_sales_day(transactions):
    """Returns (date, revenue, transaction_count) for highest revenue day"""
    daily_stats = daily_sales_trend(transactions)
    peak_date = max(daily_stats.items(), key=lambda x: x[1]['revenue'])
    return (peak_date[0], round(peak_date[1]['revenue'], 2), peak_date[1]['transaction_count'])


def low_performing_products(transactions, threshold=10):
    """Products with total quantity < threshold, sorted ascending by quantity"""
    product_stats = {}
    
    for trans in transactions:
        product = trans['ProductName']
        qty = trans['Quantity']
        revenue = qty * trans['UnitPrice']
        
        if product not in product_stats:
            product_stats[product] = {'total_qty': 0, 'total_revenue': 0.0}
        product_stats[product]['total_qty'] += qty
        product_stats[product]['total_revenue'] += revenue
    
    low_performers = [
        (name, stats['total_qty'], round(stats['total_revenue'], 2))
        for name, stats in product_stats.items()
        if stats['total_qty'] < threshold
    ]
    low_performers.sort(key=lambda x: x[1])
    return low_performers


if __name__ == "__main__":
    """Test all functions - only runs when file executed directly"""
    try:
        from file_handler import read_sales_data, parse_transactions, validate_and_filter
        print("=== PART 2: Data Processing Complete ===")
        
        raw_lines = read_sales_data('sales_data.txt')
        transactions = parse_transactions(raw_lines)
        valid_trans, _, _ = validate_and_filter(transactions)
        
        print(f"Total Revenue: ${calculate_total_revenue(valid_trans):,.2f}")
        print("Region Sales:", list(region_wise_sales(valid_trans).items())[:2])
        print("Top Products:", top_selling_products(valid_trans, 3))
        print("Peak Day:", find_peak_sales_day(valid_trans))
        print("Low Performers:", low_performing_products(valid_trans))
        
    except ImportError:
        print("Run Part 1 first or test functions individually")