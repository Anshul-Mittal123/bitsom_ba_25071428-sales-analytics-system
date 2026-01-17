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

## Run Pipeline
```bash
pip install requests
python -c "
from utils.file_handler import *;from utils.api_handler import *;from utils.report_generator import *
raw=read_sales_data('sales_data.txt');txns=parse_transactions(raw);valid,_,_=validate_and_filter(txns)
api_prods=fetch_all_products();mapping=create_product_mapping(api_prods);enriched=enrich_sales_data(valid,mapping)
generate_sales_report(valid,enriched)"
