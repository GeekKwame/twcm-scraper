# Terry White Chemmart Web Scraper

A comprehensive web scraping tool designed to extract skincare product data from Terry White Chemmart's website, with advanced ingredient analysis and grouping capabilities.

## 🚀 Features

- **Automated Product Discovery**: Intelligently searches for skincare products using multiple search strategies
- **Comprehensive Data Extraction**: Extracts detailed product information including names, brands, prices, ingredients, and more
- **Smart Fallback Mechanisms**: Multiple fallback strategies ensure maximum product discovery
- **Ingredient Analysis**: Advanced ingredient grouping and analysis capabilities
- **Multiple Output Formats**: Supports both Excel (.xlsx) and JSON output formats
- **Anti-Detection Features**: Built-in measures to avoid bot detection
- **Robust Error Handling**: Comprehensive error handling and recovery mechanisms

## 📋 Extracted Data Fields

The scraper extracts the following information for each product:

- **Product ID**: Unique identifier extracted from URL
- **Product Name**: Full product name
- **Product Line Name**: Product series or collection
- **Brand Name**: Manufacturer brand
- **Product Description**: Detailed product description
- **Product Images**: URLs of product images
- **Barcode (EAN/UPC)**: Product barcode or SKU
- **Price**: Current product price
- **Size/Volume**: Product size or volume
- **Ingredients**: Complete ingredient list
- **Skin Concern**: Targeted skin concerns
- **Source URL**: Original product page URL

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Google Chrome browser
- ChromeDriver (automatically managed by the script)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Web-Scraper
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv twc_scraper_env
   
   # On Windows
   twc_scraper_env\Scripts\activate
   
   # On macOS/Linux
   source twc_scraper_env/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

### Basic Usage

Run the scraper with default settings:

```bash
python scraper.py
```

### Advanced Usage

```python
from scraper import TWCMScraper

# Initialize scraper
scraper = TWCMScraper(headless=True)  # Set headless=True for background operation

# Scrape products (minimum 10 products)
scraper.scrape_products(min_products=15)

# Save results
scraper.save_to_excel("my_products.xlsx")
scraper.save_to_json("my_products.json")

# Close browser
scraper.close()
```

### Ingredient Analysis

Run the ingredient grouping analysis:

```bash
python ingredient_grouping.py
```

This will generate:
- Excel file with detailed analysis
- CSV files for individual components
- Visualization charts
- Comprehensive documentation

## 📁 Project Structure

```
Web-Scraper/
├── scraper.py                           # Main web scraper
├── ingredient_grouping.py               # Ingredient analysis tool
├── ingredient_grouping copy.py          # Backup of analysis tool
├── requirements.txt                     # Python dependencies
├── PART2_DOCUMENTATION.md              # Detailed documentation
├── chromedriver-win64/                  # ChromeDriver binary
│   ├── chromedriver.exe
│   ├── LICENSE.chromedriver
│   └── THIRD_PARTY_NOTICES.chromedriver
└── twc_scraper_env/                     # Virtual environment
```

## 🔧 Configuration

### ChromeDriver Setup

The scraper automatically handles ChromeDriver setup with multiple fallback strategies:

1. **Selenium Manager** (built into Selenium 4.6+)
2. **WebDriver Manager** (automatic download)
3. **Local ChromeDriver** (included in repository)

### Search Configuration

The scraper uses multiple search strategies:

- **Search Terms**: skin care, skincare, face, moisturiser, cleanser, sunscreen, etc.
- **Category Pages**: Collections and category-specific URLs
- **Sitemap Parsing**: Automatic discovery via XML sitemaps
- **URL Variations**: Multiple base URL formats

## 📊 Output Files

### Excel Output (`twcm_skincare_products.xlsx`)
- Structured data with all extracted fields
- Ready for analysis and reporting

### JSON Output (`twcm_skincare_products.json`)
- Machine-readable format
- Preserves data structure and types
- Easy integration with other tools

### Ingredient Analysis Output
- `ingredient_grouping_analysis.xlsx`: Complete analysis workbook
- `ingredient_groups.csv`: Grouped products summary
- `detailed_ingredient_matches.csv`: Detailed pair analysis
- `ingredient_frequency.csv`: Ingredient frequency data
- `ingredient_analysis.png`: Visualization charts

## 🎯 Key Features Explained

### Intelligent Product Discovery

The scraper uses a multi-layered approach to find products:

1. **Search-based Discovery**: Uses relevant skincare search terms
2. **Category Exploration**: Navigates through product categories
3. **Collection Discovery**: Automatically finds and explores collections
4. **Sitemap Parsing**: Extracts products from XML sitemaps

### Robust Data Extraction

Each product page is processed with multiple extraction methods:

- **Multiple Selectors**: Uses various CSS selectors for each field
- **Fallback Strategies**: Multiple extraction methods per field
- **Content Validation**: Ensures data quality and completeness
- **Error Recovery**: Continues processing even if individual fields fail

### Anti-Detection Measures

- **Random Delays**: Variable wait times between requests
- **User Agent Rotation**: Modern Chrome user agent
- **Browser Automation Hiding**: Removes automation indicators
- **Natural Scrolling**: Simulates human browsing behavior

## 📈 Performance

- **Processing Speed**: ~2-4 seconds per product
- **Success Rate**: High success rate with fallback mechanisms
- **Memory Usage**: Efficient memory management for large datasets
- **Error Recovery**: Robust error handling and recovery

## 🛡️ Ethical Considerations

This scraper is designed for educational and research purposes. Please ensure you:

- Respect the website's robots.txt file
- Don't overload the server with requests
- Use reasonable delays between requests
- Comply with the website's terms of service
- Consider reaching out to the website owner for permission for large-scale scraping

## 🐛 Troubleshooting

### Common Issues

1. **ChromeDriver Issues**:
   ```bash
   # Update Chrome browser
   # The scraper will automatically handle ChromeDriver
   ```

2. **Network Timeouts**:
   ```python
   # Increase wait times in the scraper
   scraper.wait = WebDriverWait(scraper.driver, 30)
   ```

3. **Missing Products**:
   ```python
   # Increase minimum products
   scraper.scrape_products(min_products=20)
   ```

### Debug Mode

Run with headless=False to see the browser in action:

```python
scraper = TWCMScraper(headless=False)
```

## 📚 Dependencies

- **selenium**: Web browser automation
- **beautifulsoup4**: HTML parsing
- **requests**: HTTP requests
- **pandas**: Data manipulation and analysis
- **openpyxl**: Excel file handling
- **matplotlib**: Data visualization
- **seaborn**: Statistical data visualization
- **lxml**: XML/HTML processing
- **webdriver-manager**: ChromeDriver management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational purposes. Please respect the terms of service of the websites you scrape.

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Review the PART2_DOCUMENTATION.md for detailed analysis
3. Open an issue in the repository

## 🔮 Future Enhancements

- [ ] Database integration
- [ ] Real-time monitoring
- [ ] Advanced ingredient analysis
- [ ] Price tracking
- [ ] API development
- [ ] Multi-site support
- [ ] Machine learning integration

---

**Note**: This tool is designed for educational and research purposes. Always respect website terms of service and implement appropriate rate limiting.
