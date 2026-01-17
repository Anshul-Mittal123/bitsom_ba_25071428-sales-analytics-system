# utils/report_generator.py - COMPLETE Part 4

from datetime import datetime
import os

def _format_currency(amount):
    """Format currency with Indian comma style"""
    return f"₹{amount:,.2f}"

def generate_sales_report(transactions, enriched_transactions, output_file='output/sales_report.txt'):
    """
    Generates a comprehensive formatted text report

    Report Must Include (in this order):
    1. HEADER - Report title, Generation date and time, Total records processed
    2. OVERALL SUMMARY - Total Revenue, Total Transactions, Average Order Value, Date Range
    3. REGION-WISE PERFORMANCE - Table with Sales, % of Total, Transactions (descending)
    4. TOP 5 PRODUCTS - Rank, Product Name, Quantity Sold, Revenue
    5. TOP 5 CUSTOMERS - Rank, Customer ID, Total Spent, Order Count
    6. DAILY SALES TREND - Date, Revenue, Transactions, Unique Customers
    7. PRODUCT PERFORMANCE ANALYSIS - Best selling day, Low performing products, Avg txn per region
    8. API ENRICHMENT SUMMARY - Total enriched, Success rate, Unmatched products
    """
    
    # Safety checks
    if not transactions:
        transactions = []
    
    # 1. HEADER
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_records = len(transactions)
    
    # 2. OVERALL SUMMARY
    total_revenue = sum(t['Quantity'] * t['UnitPrice'] for t in transactions)
    total_transactions = len(transactions)
    avg_order_value = total_revenue / total_transactions if total_transactions else 0
    dates = sorted({t['Date'] for t in transactions})
    date_range = f"{dates[0]} to {dates[-1]}" if dates else "N/A"
    
    # 3. REGION-WISE PERFORMANCE
    region_stats = {}
    for t in transactions:
        region = t['Region']
        amount = t['Quantity'] * t['UnitPrice']
        if region not in region_stats:
            region_stats[region] = {'total_sales': 0, 'transaction_count': 0}
        region_stats[region]['total_sales'] += amount
        region_stats[region]['transaction_count'] += 1
    
    # Add percentages & sort
    for region in region_stats:
        region_stats[region]['percentage'] = (
            region_stats[region]['total_sales'] / total_revenue * 100
        )
    region_stats = dict(sorted(region_stats.items(), key=lambda x: x[1]['total_sales'], reverse=True))
    
    # 4. TOP 5 PRODUCTS
    product_stats = {}
    for t in transactions:
        product = t['ProductName']
        qty = t['Quantity']
        revenue = qty * t['UnitPrice']
        if product not in product_stats:
            product_stats[product] = {'qty': 0, 'revenue': 0}
        product_stats[product]['qty'] += qty
        product_stats[product]['revenue'] += revenue
    
    top_products = sorted(product_stats.items(), key=lambda x: x[1]['qty'], reverse=True)[:5]
    
    # 5. TOP 5 CUSTOMERS
    customer_stats = {}
    for t in transactions:
        customer = t['CustomerID']
        amount = t['Quantity'] * t['UnitPrice']
        if customer not in customer_stats:
            customer_stats[customer] = {'spent': 0, 'count': 0}
        customer_stats[customer]['spent'] += amount
        customer_stats[customer]['count'] += 1
    
    top_customers = sorted(customer_stats.items(), key=lambda x: x[1]['spent'], reverse=True)[:5]
    
    # 6. DAILY SALES TREND
    daily_stats = {}
    for t in transactions:
        date = t['Date']
        customer = t['CustomerID']
        amount = t['Quantity'] * t['UnitPrice']
        if date not in daily_stats:
            daily_stats[date] = {'revenue': 0, 'count': 0, 'customers': set()}
        daily_stats[date]['revenue'] += amount
        daily_stats[date]['count'] += 1
        daily_stats[date]['customers'].add(customer)
    
    for date in daily_stats:
        daily_stats[date]['unique_customers'] = len(daily_stats[date]['customers'])
    daily_stats = dict(sorted(daily_stats.items()))
    
    # 7. PRODUCT PERFORMANCE
    peak_day = max(daily_stats.items(), key=lambda x: x[1]['revenue']) if daily_stats else ("N/A", {})
    low_products = [(name, stats['qty'], stats['revenue']) for name, stats in product_stats.items() 
                   if stats['qty'] < 10]
    low_products.sort(key=lambda x: x[1])
    
    region_avg = {r: stats['total_sales']/stats['transaction_count'] 
                 for r, stats in region_stats.items()}
    
    # 8. API ENRICHMENT SUMMARY
    total_enriched = len(enriched_transactions)
    matches = sum(1 for t in enriched_transactions if t.get('API_Match', False))
    success_rate = (matches / total_enriched * 100) if total_enriched else 0
    unmatched = sorted({t['ProductID'] for t in enriched_transactions if not t.get('API_Match', False)})
    
    # CREATE OUTPUT DIRECTORY & FILE
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # ===== 1. HEADER =====
        f.write("=" * 47 + "\n")
        f.write("          SALES ANALYTICS REPORT\n")
        f.write(f"        Generated: {generated_at}\n")
        f.write(f"        Records Processed: {total_records}\n")
        f.write("=" * 47 + "\n\n")
        
        # ===== 2. OVERALL SUMMARY =====
        f.write("OVERALL SUMMARY\n")
        f.write("-" * 44 + "\n")
        f.write(f"Total Revenue:        {_format_currency(total_revenue)}\n")
        f.write(f"Total Transactions:   {total_transactions}\n")
        f.write(f"Average Order Value:  {_format_currency(avg_order_value)}\n")
        f.write(f"Date Range:           {date_range}\n\n")
        
        # ===== 3. REGION-WISE PERFORMANCE =====
        f.write("REGION-WISE PERFORMANCE\n")
        f.write("-" * 44 + "\n")
        f.write(f"{'Region':<10}{'Sales':>15}{'% of Total':>13}{'Transactions':>15}\n")
        f.write("-" * 44 + "\n")
        for region, stats in region_stats.items():
            f.write(f"{region:<10}{_format_currency(stats['total_sales']):>15}"
                   f"{stats['percentage']:>10.1f}%{stats['transaction_count']:>15}\n")
        f.write("\n")
        
        # ===== 4. TOP 5 PRODUCTS =====
        f.write("TOP 5 PRODUCTS\n")
        f.write("-" * 44 + "\n")
        f.write(f"{'Rank':<6}{'Product Name':<25}{'Quantity Sold':>15}{'Revenue':>15}\n")
        f.write("-" * 44 + "\n")
        for i, (name, stats) in enumerate(top_products, 1):
            f.write(f"{i:<6}{name[:24]:<25}{stats['qty']:>15}{_format_currency(stats['revenue']):>15}\n")
        f.write("\n")
        
        # ===== 5. TOP 5 CUSTOMERS =====
        f.write("TOP 5 CUSTOMERS\n")
        f.write("-" * 44 + "\n")
        f.write(f"{'Rank':<6}{'Customer ID':<15}{'Total Spent':>15}{'Order Count':>15}\n")
        f.write("-" * 44 + "\n")
        for i, (cust_id, stats) in enumerate(top_customers, 1):
            f.write(f"{i:<6}{cust_id:<15}{_format_currency(stats['spent']):>15}{stats['count']:>15}\n")
        f.write("\n")
        
        # ===== 6. DAILY SALES TREND =====
        f.write("DAILY SALES TREND\n")
        f.write("-" * 44 + "\n")
        f.write(f"{'Date':<12}{'Revenue':>15}{'Transactions':>15}{'Unique Customers':>20}\n")
        f.write("-" * 44 + "\n")
        for date, stats in list(daily_stats.items())[:12]:  # Show first 12 days
            f.write(f"{date:<12}{_format_currency(stats['revenue']):>15}"
                   f"{stats['count']:>15}{stats['unique_customers']:>20}\n")
        if len(daily_stats) > 12:
            f.write(f"... and {len(daily_stats)-12} more days\n")
        f.write("\n")
        
        # ===== 7. PRODUCT PERFORMANCE ANALYSIS =====
        f.write("PRODUCT PERFORMANCE ANALYSIS\n")
        f.write("-" * 44 + "\n")
        peak_date, peak_stats = peak_day
        f.write(f"Best Selling Day: {peak_date}\n")
        f.write(f"Revenue: {_format_currency(peak_stats['revenue'])} | "
               f"Transactions: {peak_stats['count']}\n\n")
        
        f.write("Low Performing Products (Quantity < 10):\n")
        if low_products:
            for name, qty, rev in low_products[:8]:
                f.write(f"  {name[:25]:<25} {qty:>5} units  {_format_currency(rev)}\n")
        else:
            f.write("  None\n\n")
        
        f.write("Average Transaction Value per Region:\n")
        for region, avg_val in sorted(region_avg.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {region:<12}{_format_currency(avg_val)}\n")
        f.write("\n")
        
        # ===== 8. API ENRICHMENT SUMMARY =====
        f.write("API ENRICHMENT SUMMARY\n")
        f.write("-" * 44 + "\n")
        f.write(f"Total Products Enriched:  {total_enriched}\n")
        f.write(f"Success Rate:             {success_rate:.1f}%\n")
        f.write("Products that couldn't be enriched:\n")
        if unmatched:
            for pid in unmatched[:15]:
                f.write(f"  - {pid}\n")
            if len(unmatched) > 15:
                f.write(f"  ... and {len(unmatched)-15} more\n")
        else:
            f.write("  - None\n")
    
    print(f"✅ Sales report generated: {output_file}")

# Test function (runs only when file executed directly)
if __name__ == "__main__":
    print("Testing report generation...")
    # This would normally import from other parts
    # For standalone testing, create dummy data
    dummy_transactions = [
        {'TransactionID': 'T001', 'Date': '2024-12-01', 'ProductID': 'P101', 
         'ProductName': 'Laptop', 'Quantity': 2, 'UnitPrice': 45000, 
         'CustomerID': 'C001', 'Region': 'North'}
    ]
    dummy_enriched = [
        {'TransactionID': 'T001', 'Date': '2024-12-01', 'ProductID': 'P101', 
         'ProductName': 'Laptop', 'Quantity': 2, 'UnitPrice': 45000, 
         'CustomerID': 'C001', 'Region': 'North', 'API_Match': True}
    ]
    generate_sales_report(dummy_transactions, dummy_enriched)