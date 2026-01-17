# Sales Analytics System

## Structure
├── sales_data.txt
├── utils/
│ ├── file_handler.py # Part 1
│ ├── data_processor.py # Part 2
│ ├── api_handler.py # Part 3
│ └── report_generator.py # Part 4
├── data/ # sales_data.txt
└── output/ # sales_report.txt

## Console Run 
===========================================
SALES ANALYTICS SYSTEM
===========================================
[1/10] Reading sales data...
✓ Successfully read 95 raw lines

[2/10] Parsing and cleaning data...
✓ Parsed 92 transactions

[3/10] Filter Options Available:
Regions: East, North, South, West
Amount Range: ₹500 - ₹90,000

Do you want to filter data? (y/n): n

[4/10] Final dataset: 92 valid transactions

[5/10] Analyzing sales data...
✓ Analysis complete

[6/10] Fetching product data from API...
✓ Fetched 100 products

[8/10] Enriching sales data...
✓ Enriched 92 transactions 

[7/10] Saving enriched data...
✓ saved to: data/enriched_sales_report.txt

[9/10] Generating report...
✓ Report saved to: output/sales_report.txt

[10/10] Process Complete!

===========================================

## Run Pipeline
```bash
pip install requests
python -c "
from utils.file_handler import *;from utils.api_handler import *;from utils.report_generator import *
raw=read_sales_data('sales_data.txt');txns=parse_transactions(raw);valid,_,_=validate_and_filter(txns)
api_prods=fetch_all_products();mapping=create_product_mapping(api_prods);enriched=enrich_sales_data(valid,mapping)
generate_sales_report(valid,enriched)"
