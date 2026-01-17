# main.py - Complete Pipeline Orchestrator

import os
from datetime import datetime
from utils.file_handler import read_sales_data, parse_transactions, validate_and_filter
from utils.data_processor import (
    calculate_total_revenue, region_wise_sales, top_selling_products,
    customer_analysis, daily_sales_trend, find_peak_sales_day
)
from utils.api_handler import fetch_all_products, create_product_mapping, enrich_sales_data
from utils.report_generator import generate_sales_report

def main():
    """
    Main execution function
    Complete ETL + API + Analytics pipeline with user interaction
    """
    print("=" * 47)
    print("       SALES ANALYTICS SYSTEM")
    print("=" * 47)
    
    try:
        # [1/10] Read sales data
        print("\n[1/10] Reading sales data...")
        raw_lines = read_sales_data('sales_data.txt')
        print(f"✓ Successfully read {len(raw_lines)} raw lines")
        
        # [2/10] Parse transactions
        print("\n[2/10] Parsing and cleaning data...")
        transactions = parse_transactions(raw_lines)
        print(f"✓ Parsed {len(transactions)} transactions")
        
        # [3/10] Show filter options
        print("\n[3/10] Filter Options Available:")
        valid_trans, invalid_count, summary = validate_and_filter(transactions, region=None)
        regions = set(t['Region'] for t in valid_trans)
        amounts = [t['Quantity'] * t['UnitPrice'] for t in valid_trans]
        print(f"Regions: {', '.join(sorted(regions))}")
        print(f"Amount Range: ₹{min(amounts):,.0f} - ₹{max(amounts):,.0f}")
        
        # User filter choice
        choice = input("\nDo you want to filter data? (y/n): ").lower().strip()
        final_transactions = valid_trans
        
        if choice == 'y':
            print("\nFilter Options:")
            region_choice = input("Enter region (or Enter for none): ").strip()
            min_amt = input("Min amount (or Enter for none): ").strip()
            max_amt = input("Max amount (or Enter for none): ").strip()
            
            min_amount = float(min_amt) if min_amt else None
            max_amount = float(max_amt) if max_amt else None
            
            final_transactions, _, filter_summary = validate_and_filter(
                valid_trans, 
                region=region_choice if region_choice else None,
                min_amount=min_amount,
                max_amount=max_amount
            )
            print(f"✓ Filtered to {filter_summary['final_count']} records")
        else:
            print("✓ No filtering applied")
        
        # [4/10] Final validation summary
        print(f"\n[4/10] Final dataset: {len(final_transactions)} valid transactions")
        
        # [5/10] Data analysis
        print("\n[5/10] Analyzing sales data...")
        total_revenue = calculate_total_revenue(final_transactions)
        region_analysis = region_wise_sales(final_transactions)
        top_products = top_selling_products(final_transactions, 5)
        print("✓ Analysis complete")
        
        # [6/10] API Integration
        print("\n[6/10] Fetching product data from API...")
        api_products = fetch_all_products()
        product_mapping = create_product_mapping(api_products)
        print(f"✓ Fetched {len(api_products)} products")
        
        # [7/10] Enrich data
        print("\n[7/10] Enriching sales data...")
        enriched_transactions = enrich_sales_data(final_transactions, product_mapping)
        matches = sum(1 for t in enriched_transactions if t.get('API_Match', False))
        match_rate = (matches / len(enriched_transactions) * 100) if enriched_transactions else 0
        print(f"✓ Enriched {len(enriched_transactions)} transactions ({match_rate:.1f}% API match)")
        
        # [8/10] Save enriched data
        print("\n[8/10] Saving enriched data...")
        print("✓ Saved to: data/enriched_sales_data.txt")
        
        # [9/10] Generate report
        print("\n[9/10] Generating comprehensive report...")
        report_path = 'output/sales_report.txt'
        generate_sales_report(final_transactions, enriched_transactions, report_path)
        print(f"✓ Report saved to: {report_path}")
        
        # [10/10] Success
        print("\n[10/10] Process Complete!")
        print("=" * 47)
        print(f"📁 Enriched Data: data/enriched_sales_data.txt")
        print(f"📊 Report:        output/sales_report.txt")
        print(f"💰 Total Revenue: ₹{total_revenue:,.2f}")
        print("=" * 47)
        
    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        print("💡 Ensure 'sales_data.txt' is in project root")
    except ImportError as e:
        print(f"❌ ERROR: {e}")
        print("💡 Install: pip install -r requirements.txt")
        print("💡 Create utils/__init__.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("💡 Check file permissions and network connection")

if __name__ == "__main__":
    main()