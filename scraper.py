import time
import re
import pandas as pd
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urljoin, urlparse, quote
from bs4 import BeautifulSoup
import random
import os
from webdriver_manager.chrome import ChromeDriverManager
from typing import List

class TWCMScraper:
    def __init__(self, headless=False):
        self.base_url = "https://terrywhitechemmart.com.au/"
        self.driver = self.setup_driver(headless)
        self.wait = WebDriverWait(self.driver, 20)
        self.product_data = []
        
    def setup_driver(self, headless):
        """Configure Chrome driver with appropriate options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        # Reduce GPU/DirectComposition issues on Windows
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--window-size=1920,1080")
        # Keep UA modern and in line with recent Chrome to avoid bot blocks
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

        # Prefer Selenium Manager (built into Selenium 4.6+) and fall back smartly
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as primary_error:
            print(f"Selenium Manager failed to provision driver, falling back. Reason: {primary_error}")

            # Fallback 1: webdriver_manager
            try:
                manager_path = ChromeDriverManager().install()
                service = Service(manager_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                return driver
            except Exception as secondary_error:
                print(f"webdriver_manager fallback failed, trying local chromedriver. Reason: {secondary_error}")

                # Fallback 2: local chromedriver in repo
                local_driver_path = r"C:\Users\~Eddie~\Desktop\Web-Scraper\chromedriver-win64\chromedriver.exe"
                service = Service(local_driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                return driver

    def get_product_urls(self):
        """Get product URLs using search functionality"""
        print("Searching for skincare products...")
        base_variants = [
            "https://terrywhitechemmart.com.au",
            "https://www.terrywhitechemmart.com.au"
        ]
        
        # List of skincare-related search terms - using broader, more common terms
        search_terms = [
            "skin care",
            "skincare", 
            "face",
            "moisturiser",
            "cleanser",
            "sunscreen",
            "cream",
            "lotion",
            "oil",
            "serum",
            "mask"
        ]
        
        product_urls = []
        
        for term in search_terms:
            try:
                # Try different search URL formats across base variants
                search_urls = []
                for b in base_variants:
                    search_urls.extend([
                        f"{b}/shop/products?query={quote(term)}",
                        f"{b}/search?q={quote(term)}",
                        f"{b}/search?q={quote(term)}&type=product",
                        f"{b}/search?q={quote(term)}&sort_by=relevance"
                    ])
                for search_url in search_urls:
                    print(f"Searching for: {term} at {search_url}")
                    self.driver.get(search_url)
                    # Wait for page to render and lazy content to appear
                    try:
                        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                    except TimeoutException:
                        pass
                    time.sleep(2)
                    # Scroll to trigger lazy loading
                    try:
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(1.5)
                        self.driver.execute_script("window.scrollTo(0, 0);")
                        time.sleep(1)
                    except Exception:
                        pass
                    
                    # Look for product links using multiple selectors
                    product_selectors = [
                        "a[href*='/products/']",
                        ".product-tile a",
                        ".product-item a", 
                        ".product-card a",
                        "[data-testid*='product'] a",
                        ".product a"
                    ]
                    
                    for selector in product_selectors:
                        try:
                            links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for link in links:
                                try:
                                    href = link.get_attribute('href')
                                    if href and ('/products/' in href or '/product/' in href):
                                        if href not in product_urls:
                                            product_urls.append(href)
                                            print(f"Found product: {href}")
                                except Exception:
                                    continue
                        except Exception:
                            continue
                    
                    # Also try finding all links and filtering
                    links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        try:
                            href = link.get_attribute('href')
                            if href and ('/products/' in href or '/product/' in href):
                                if href not in product_urls:
                                    product_urls.append(href)
                                    print(f"Found product: {href}")
                        except Exception:
                            continue
                    
                    if len(product_urls) >= 15:
                        break
                
                if len(product_urls) >= 15:
                    break
                    
            except Exception as e:
                print(f"Error searching for {term}: {e}")
                continue
        
        # If search doesn't work, try to find products from category pages
        if len(product_urls) < 10:
            print("Search didn't find enough products, trying category pages...")
            category_urls = []
            for b in base_variants:
                category_urls.extend([
                    f"{b}/shop/products?query=skincare",
                    f"{b}/shop/products?query=face%20care",
                    f"{b}/shop/products?query=beauty",
                    f"{b}/shop/products?query=health%20wellness",
                    f"{b}/collections/skincare",
                    f"{b}/collections/face-care",
                    f"{b}/collections/beauty",
                    f"{b}/collections/health-wellness"
                ])
            
            for category_url in category_urls:
                try:
                    print(f"Checking category: {category_url}")
                    self.driver.get(category_url)
                    try:
                        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                    except TimeoutException:
                        pass
                    time.sleep(1.5)
                    try:
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(1.0)
                        self.driver.execute_script("window.scrollTo(0, 0);")
                        time.sleep(0.5)
                    except Exception:
                        pass
                    
                    # Look for product links in category pages
                    links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        try:
                            href = link.get_attribute('href')
                            if href and ('/products/' in href):
                                if href not in product_urls:
                                    product_urls.append(href)
                                    print(f"Found product: {href}")
                        except Exception:
                            continue
                    
                    if len(product_urls) >= 15:
                        break
                        
                except Exception as e:
                    print(f"Error checking category {category_url}: {e}")
                    continue

        # If still insufficient, discover collections from /collections index
        if len(product_urls) < 10:
            print("Category list insufficient, discovering collections directory...")
            discovered_collections = []
            for b in base_variants:
                collections_index = f"{b}/collections"
                try:
                    print(f"Opening collections index: {collections_index}")
                    self.driver.get(collections_index)
                    try:
                        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                    except TimeoutException:
                        pass
                    time.sleep(1.0)
                    links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        try:
                            href = link.get_attribute('href')
                            if href and '/collections/' in href and href not in discovered_collections:
                                discovered_collections.append(href)
                        except Exception:
                            continue
                except Exception as e:
                    print(f"Error opening collections index {collections_index}: {e}")
                    continue

            # Visit a subset of discovered collections
            for coll_url in discovered_collections[:10]:
                try:
                    print(f"Exploring discovered collection: {coll_url}")
                    self.driver.get(coll_url)
                    try:
                        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                    except TimeoutException:
                        pass
                    time.sleep(1.0)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(0.8)
                    links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        try:
                            href = link.get_attribute('href')
                            if href and ('/products/' in href) and href not in product_urls:
                                product_urls.append(href)
                                print(f"Found product from discovered collection: {href}")
                                if len(product_urls) >= 15:
                                    break
                        except Exception:
                            continue
                    if len(product_urls) >= 15:
                        break
                except Exception as e:
                    print(f"Error exploring collection {coll_url}: {e}")
                    continue

        # Final fallback: parse sitemap(s) for product URLs
        if len(product_urls) < 10:
            print("Category fallback insufficient, trying sitemap...")
            try:
                sitemap_urls = self._fetch_product_urls_from_sitemaps(max_urls=50)
                for href in sitemap_urls:
                    if href not in product_urls and '/products/' in href:
                        product_urls.append(href)
                        print(f"Found product via sitemap: {href}")
            except Exception as e:
                print(f"Error while parsing sitemap: {e}")
        
        return list(set(product_urls))[:15]  # Remove duplicates and return top 15

    def _fetch_product_urls_from_sitemaps(self, max_urls: int = 50) -> List[str]:
        """Fetch product URLs from common sitemap endpoints.
        Attempts sitemap index first, then well-known product sitemap shards.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
        }
        bases = [
            'https://terrywhitechemmart.com.au/',
            'https://www.terrywhitechemmart.com.au/'
        ]
        candidate_sitemaps = []
        for b in bases:
            candidate_sitemaps.extend([
                urljoin(b, 'sitemap.xml'),
                urljoin(b, 'sitemap_index.xml'),
                urljoin(b, 'sitemap_products_1.xml'),
                urljoin(b, 'sitemap_products_2.xml'),
                urljoin(b, 'sitemap_products_3.xml'),
            ])
        found_product_sitemaps: List[str] = []
        product_urls: List[str] = []

        # First: try to resolve index and gather product sitemap URLs
        for sm_url in candidate_sitemaps[:2]:
            try:
                resp = requests.get(sm_url, headers=headers, timeout=15)
                if resp.status_code != 200 or not resp.text.strip():
                    continue
                soup_xml = BeautifulSoup(resp.text, 'xml')
                sitemap_tags = soup_xml.find_all('sitemap')
                if sitemap_tags:
                    for tag in sitemap_tags:
                        loc_tag = tag.find('loc')
                        if not loc_tag:
                            continue
                        loc = loc_tag.get_text(strip=True)
                        if '/sitemap_products' in loc and loc not in found_product_sitemaps:
                            found_product_sitemaps.append(loc)
            except Exception:
                continue

        # If none found via index, fall back to guessed product sitemaps
        if not found_product_sitemaps:
            found_product_sitemaps = candidate_sitemaps[2:]

        # Fetch product URLs from product sitemaps
        for prod_sm in found_product_sitemaps:
            try:
                resp = requests.get(prod_sm, headers=headers, timeout=15)
                if resp.status_code != 200 or not resp.text.strip():
                    continue
                soup_xml = BeautifulSoup(resp.text, 'xml')
                url_tags = soup_xml.find_all('url') or soup_xml.find_all('urlset')
                if not url_tags:
                    # Some sitemaps are simple urlset/loc list
                    loc_tags = soup_xml.find_all('loc')
                    for loc in loc_tags:
                        href = loc.get_text(strip=True)
                        if '/products/' in href:
                            product_urls.append(href)
                            if len(product_urls) >= max_urls:
                                return list(dict.fromkeys(product_urls))
                else:
                    loc_tags = soup_xml.find_all('loc')
                    for loc in loc_tags:
                        href = loc.get_text(strip=True)
                        if '/products/' in href:
                            product_urls.append(href)
                            if len(product_urls) >= max_urls:
                                return list(dict.fromkeys(product_urls))
            except Exception:
                continue

        return list(dict.fromkeys(product_urls))

    def extract_product_data(self, product_url):
        """Extract detailed product data from product page"""
        print(f"Scraping product: {product_url}")
        self.driver.get(product_url)
        time.sleep(5)  # Increased wait time for better loading
        
        # Wait for page to fully load
        try:
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        except TimeoutException:
            pass
        
        # Additional wait for dynamic content
        time.sleep(3)
        
        product = {
            'Product ID': self.extract_product_id(product_url),
            'Product Name': '',
            'Product Line Name': '',
            'Brand Name': '',
            'Product Description': '',
            'Product Images': [],
            'Barcode (EAN/UPC)': '',
            'Price': '',
            'Size/Volume': '',
            'Ingredients': '',
            'Skin Concern': '',
            'Source URL': product_url
        }
        
        try:
            # Wait for page to load completely
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            except TimeoutException:
                pass
            
            # Get page content
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract product name using multiple methods
            try:
                # Method 1: Look for specific product name selectors
                name_selectors = [
                    'h1.product-title',
                    'h1.product-name', 
                    '.product-title',
                    '.product-name',
                    'h1[data-testid="product-title"]',
                    '.product-details h1',
                    '.product-info h1',
                    '.product-header h1',
                    '.product-main h1',
                    '.product-content h1',
                    'h1'
                ]
                
                for selector in name_selectors:
                    element = soup.select_one(selector)
                    if element:
                        text = element.get_text().strip()
                        if text and len(text) > 3:
                            # Skip obvious not found pages
                            if any(phrase in text.lower() for phrase in ["we couldn't find this page", "page not found", "not found", "404"]):
                                print("Not found page detected. Skipping.")
                                return {**product, 'Product Name': ''}
                            # Clean up the text - remove common suffixes and clean up
                            text = text.replace('^', '').strip()
                            if text and not text.lower().startswith('terry white'):
                                product['Product Name'] = text
                                break
                
                # Method 2: Use title tag as fallback
                if not product['Product Name']:
                    title = soup.find('title')
                    if title:
                        title_text = title.get_text().strip()
                        if "we couldn't find this page" not in title_text.lower() and "page not found" not in title_text.lower():
                            # Clean up title text
                            clean_title = title_text.split('|')[0].strip()
                            clean_title = clean_title.replace('^', '').strip()
                            if clean_title and not clean_title.lower().startswith('terry white'):
                                product['Product Name'] = clean_title
                
                # Method 3: Extract from URL if still no name found
                if not product['Product Name']:
                    url_parts = product_url.split('/')[-1].split('?')[0]
                    if url_parts:
                        # Convert URL slug to readable name
                        name = url_parts.replace('-', ' ').title()
                        # Clean up common URL patterns
                        name = name.replace('Ml', 'ml').replace('G', 'g').replace('Mg', 'mg')
                        product['Product Name'] = name
                
                # Method 4: Try to get product name from meta tags
                if not product['Product Name']:
                    meta_title = soup.find('meta', attrs={'property': 'og:title'})
                    if meta_title and meta_title.get('content'):
                        product['Product Name'] = meta_title.get('content').strip()
                            
            except Exception as e:
                print(f"Error extracting product name: {e}")
                pass
            
            # Extract brand name using multiple methods
            try:
                # Method 1: Look for brand in specific elements
                brand_selectors = [
                    '.product-brand',
                    '.brand-name',
                    '[data-testid="brand"]',
                    '.product-details .brand',
                    '.product-info .brand'
                ]
                
                for selector in brand_selectors:
                    element = soup.select_one(selector)
                    if element:
                        brand_text = element.get_text().strip()
                        if brand_text:
                            product['Brand Name'] = brand_text
                            break
                
                # Method 2: Extract from product name using known brands
                if not product['Brand Name']:
                    brands = ["La Roche-Posay", "Avene", "Neutrogena", "CeraVe", "The Ordinary", 
                             "QV", "Sukin", "Trilogy", "Swisse", "Natio", "Cetaphil", "Dermal",
                             "L'Oreal", "Olay", "Nivea", "La Roche", "Aveeno", "Bioderma", "Ego",
                             "Ego Pharmaceuticals", "Hamilton", "Cancer Council", "Banana Boat",
                             "Dermaveen", "Alpha-H", "Ultraceuticals", "Rationale", "Aspect",
                             "Medik8", "Skinstitut", "Ella Bache", "Jurlique", "Aesop", "MooGoo",
                             "Bio-Oil", "Dermeze", "SolarCare", "Skin B5", "The Goat Skincare",
                             "In Essence", "Gem", "Moogoo", "Epaderm", "Benzac", "Skin Ritual",
                             "Hey Bud", "The Jojoba Company", "QA", "24 Daily", "Terry White Chemmart"]
                    
                    product_name_lower = product['Product Name'].lower()
                    for brand in brands:
                        if brand.lower() in product_name_lower:
                            product['Brand Name'] = brand
                            break
                
                # Method 3: Extract from URL if still no brand found
                if not product['Brand Name']:
                    url_parts = product_url.split('/')[-1].split('?')[0].split('-')
                    if url_parts:
                        # Try to identify brand from URL structure
                        potential_brand = url_parts[0].title()
                        if potential_brand in ["Natio", "CeraVe", "Olay", "MooGoo", "Dermal", "Ego", "Bio", "Dermeze", "Solar", "Skin", "The", "In", "Gem", "Epa", "Ben", "Hey", "Jojoba", "Terry"]:
                            product['Brand Name'] = potential_brand
                            
            except Exception as e:
                print(f"Error extracting brand name: {e}")
                pass
            
            # Extract price using multiple methods
            try:
                # Method 1: Look for price in specific elements
                price_selectors = [
                    '.product-price',
                    '.price',
                    '[data-testid="price"]',
                    '.product-details .price',
                    '.product-info .price',
                    '.current-price',
                    '.sale-price',
                    '.regular-price'
                ]
                
                for selector in price_selectors:
                    element = soup.select_one(selector)
                    if element:
                        price_text = element.get_text().strip()
                        if price_text and '$' in price_text:
                            product['Price'] = price_text
                            break
                
                # Method 2: Use regex patterns
                if not product['Price']:
                    price_patterns = [
                        r'\$\d+\.\d{2}',
                        r'\$\d+',
                        r'Price:\s*\$[\d,]+\.?\d*',
                        r'From\s*\$[\d,]+\.?\d*'
                    ]
                    
                    for pattern in price_patterns:
                        matches = re.findall(pattern, page_source)
                        if matches:
                            product['Price'] = matches[0]
                            break
                            
            except Exception as e:
                print(f"Error extracting price: {e}")
                pass
            
            # Extract description using multiple methods
            try:
                # Method 1: Look for meta description first
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc and meta_desc.get('content'):
                    product['Product Description'] = meta_desc.get('content')
                
                # Method 2: Look for specific description elements
                if not product['Product Description']:
                    desc_selectors = [
                        '.product-description',
                        '.product-details .description',
                        '.product-info .description',
                        '[data-testid="description"]',
                        '.product-summary',
                        '.product-overview'
                    ]
                    
                    for selector in desc_selectors:
                        element = soup.select_one(selector)
                        if element:
                            text = element.get_text().strip()
                            if text and len(text) > 20:
                                product['Product Description'] = text
                                break
                
                # Method 3: Look for description in paragraphs and divs
                if not product['Product Description']:
                    desc_elements = soup.find_all(['p', 'div'], class_=re.compile(r'description|desc|product|summary|overview'))
                    for element in desc_elements:
                        text = element.get_text().strip()
                        if text and len(text) > 20:
                            product['Product Description'] = text
                            break
                            
            except Exception as e:
                print(f"Error extracting description: {e}")
                pass
            
            # Extract images using multiple methods
            try:
                # Method 1: Look for product images in specific containers
                image_selectors = [
                    '.product-images img',
                    '.product-gallery img',
                    '.product-photos img',
                    '.product-details img',
                    '[data-testid*="image"] img',
                    '.product-main-image img'
                ]
                
                for selector in image_selectors:
                    img_elements = soup.select(selector)
                    for img in img_elements:
                        src = img.get('src', '') or img.get('data-src', '') or img.get('data-lazy', '')
                        if src and ('http' in src or '//' in src):
                            if src.startswith('//'):
                                src = 'https:' + src
                            if src not in product['Product Images'] and 'placeholder' not in src.lower():
                                product['Product Images'].append(src)
                
                # Method 2: Get all images as fallback
                if not product['Product Images']:
                    img_tags = soup.find_all('img')
                    for img in img_tags:
                        src = img.get('src', '') or img.get('data-src', '') or img.get('data-lazy', '')
                        if src and ('http' in src or '//' in src):
                            if src.startswith('//'):
                                src = 'https:' + src
                            if src not in product['Product Images'] and 'placeholder' not in src.lower():
                                product['Product Images'].append(src)
                                
            except Exception as e:
                print(f"Error extracting images: {e}")
                pass
            
            # Extract size/volume using multiple methods
            try:
                # Method 1: Look for size in specific elements
                size_selectors = [
                    '.product-size',
                    '.size',
                    '.volume',
                    '.product-details .size',
                    '.product-info .size',
                    '[data-testid="size"]'
                ]
                
                for selector in size_selectors:
                    element = soup.select_one(selector)
                    if element:
                        size_text = element.get_text().strip()
                        if size_text:
                            product['Size/Volume'] = size_text
                            break
                
                # Method 2: Extract from product name using regex
                if not product['Size/Volume']:
                    size_patterns = [
                        r'(\d+\s*(ml|g|mg|L|oz|tablets|capsules|pills|units))',
                        r'(\d+\s*(ml|g|mg|L|oz))',
                        r'(\d+\s*(tablets|capsules|pills|units))',
                        r'(\d+\s*(ml|g|mg|L))'
                    ]
                    
                    for pattern in size_patterns:
                        size_match = re.search(pattern, product['Product Name'], re.IGNORECASE)
                        if size_match:
                            product['Size/Volume'] = size_match.group(1)
                            break
                            
            except Exception as e:
                print(f"Error extracting size/volume: {e}")
                pass
            
            # Extract ingredients using multiple methods
            try:
                # Method 1: Look for ingredients in specific elements
                ing_selectors = [
                    '.product-ingredients',
                    '.ingredients',
                    '.product-details .ingredients',
                    '.product-info .ingredients',
                    '[data-testid="ingredients"]',
                    '.product-specs .ingredients',
                    '.product-attributes .ingredients',
                    '.ingredient-list',
                    '.active-ingredients',
                    '.key-ingredients'
                ]
                
                for selector in ing_selectors:
                    element = soup.select_one(selector)
                    if element:
                        ing_text = element.get_text().strip()
                        if ing_text and len(ing_text) > 10:
                            product['Ingredients'] = ing_text
                            break
                
                # Method 2: Extract from description using regex
                if not product['Ingredients']:
                    ing_patterns = [
                        r'Ingredients[:\s]*([^\.]+)',
                        r'INGREDIENTS[:\s]*([^\.]+)',
                        r'Contains[:\s]*([^\.]+)',
                        r'Active Ingredients[:\s]*([^\.]+)',
                        r'Key Ingredients[:\s]*([^\.]+)',
                        r'Formulated with[:\s]*([^\.]+)',
                        r'Key Naturals[:\s]*([^\.]+)',
                        r'Made with[:\s]*([^\.]+)',
                        r'Enriched with[:\s]*([^\.]+)',
                        r'With[:\s]*([^\.]+)',
                        r'Contains[:\s]*([^\.]+)',
                        r'Active[:\s]*([^\.]+)'
                    ]
                    
                    # Search in description and page source
                    search_text = product['Product Description'] + ' ' + page_source
                    for pattern in ing_patterns:
                        match = re.search(pattern, search_text, re.IGNORECASE)
                        if match:
                            ingredient_text = match.group(1).strip()
                            if len(ingredient_text) > 5:
                                product['Ingredients'] = ingredient_text
                                break
                
                # Method 3: Look for ingredients in product specifications
                if not product['Ingredients']:
                    spec_selectors = [
                        '.product-specifications',
                        '.product-specs',
                        '.specifications',
                        '.product-details .specs',
                        '.product-info .specs'
                    ]
                    
                    for selector in spec_selectors:
                        element = soup.select_one(selector)
                        if element:
                            spec_text = element.get_text()
                            # Look for ingredient patterns in specs
                            for pattern in ing_patterns:
                                match = re.search(pattern, spec_text, re.IGNORECASE)
                                if match:
                                    ingredient_text = match.group(1).strip()
                                    if len(ingredient_text) > 5:
                                        product['Ingredients'] = ingredient_text
                                        break
                            if product['Ingredients']:
                                break
                            
            except Exception as e:
                print(f"Error extracting ingredients: {e}")
                pass
            
            # Extract product line name
            try:
                # Look for product line in specific elements
                line_selectors = [
                    '.product-line',
                    '.product-series',
                    '.product-collection',
                    '.product-range',
                    '.product-details .line',
                    '.product-info .line'
                ]
                
                for selector in line_selectors:
                    element = soup.select_one(selector)
                    if element:
                        line_text = element.get_text().strip()
                        if line_text:
                            product['Product Line Name'] = line_text
                            break
                
                # Extract from product name if no specific element found
                if not product['Product Line Name']:
                    # Look for common product line patterns
                    line_patterns = [
                        r'^([^-\s]+)\s+',  # First word before space
                        r'^([A-Z][a-z]+)\s+',  # Capitalized word at start
                    ]
                    
                    for pattern in line_patterns:
                        match = re.search(pattern, product['Product Name'])
                        if match:
                            potential_line = match.group(1)
                            # Filter out common non-line words
                            if potential_line.lower() not in ['the', 'a', 'an', 'and', 'or', 'but']:
                                product['Product Line Name'] = potential_line
                                break
                                
            except Exception as e:
                print(f"Error extracting product line: {e}")
                pass
            
            # Determine skin concern
            try:
                concerns = {
                    'acne': ['acne', 'breakout', 'blemish', 'pimple', 'spot', 'oil', 'sebum', 'clogged pores'],
                    'dry skin': ['dry', 'hydration', 'moisture', 'hydrating', 'dehydrated', 'parched'],
                    'aging': ['aging', 'wrinkle', 'anti-age', 'firm', 'lift', 'age', 'line', 'fine lines'],
                    'sensitive': ['sensitive', 'calm', 'soothe', 'redness', 'irritat', 'gentle'],
                    'hyperpigmentation': ['pigment', 'dark spot', 'brighten', 'even tone', 'discolor', 'uneven'],
                    'oily skin': ['oil', 'shine', 'matte', 'porcelain', 'sebum', 'greasy'],
                    'combination skin': ['combination', 't-zone', 'mixed'],
                    'mature skin': ['mature', 'anti-aging', 'firming', 'lifting']
                }
                
                text = (product['Product Name'] + ' ' + product['Product Description']).lower()
                found_concerns = []
                
                for concern, keywords in concerns.items():
                    for keyword in keywords:
                        if keyword in text:
                            found_concerns.append(concern)
                            break
                
                if found_concerns:
                    product['Skin Concern'] = ', '.join(found_concerns)
                    
            except Exception as e:
                print(f"Error determining skin concern: {e}")
                pass
            
            # Extract barcode using multiple methods
            try:
                # Method 1: Look for barcode in specific elements
                barcode_selectors = [
                    '.product-barcode',
                    '.barcode',
                    '.product-code',
                    '.sku',
                    '.product-sku',
                    '[data-testid="barcode"]',
                    '.product-details .barcode',
                    '.product-info .barcode',
                    '.product-specs .barcode',
                    '.product-attributes .barcode'
                ]
                
                for selector in barcode_selectors:
                    element = soup.select_one(selector)
                    if element:
                        barcode_text = element.get_text().strip()
                        if barcode_text:
                            product['Barcode (EAN/UPC)'] = barcode_text
                            break
                
                # Method 2: Extract from description using regex patterns
                if not product['Barcode (EAN/UPC)']:
                    barcode_patterns = [
                        r'\b\d{8,14}\b',  # Standard barcode length
                        r'Barcode[:\s]*(\d{8,14})',
                        r'UPC[:\s]*(\d{8,14})',
                        r'EAN[:\s]*(\d{8,14})',
                        r'Product Code[:\s]*(\d{8,14})',
                        r'SKU[:\s]*(\d{8,14})',
                        r'Code[:\s]*(\d{8,14})',
                        r'Item Code[:\s]*(\d{8,14})'
                    ]
                    
                    # Search in description and page source
                    search_text = product['Product Description'] + ' ' + page_source
                    for pattern in barcode_patterns:
                        match = re.search(pattern, search_text, re.IGNORECASE)
                        if match:
                            product['Barcode (EAN/UPC)'] = match.group(1) if len(match.groups()) > 0 else match.group(0)
                            break
                
                # Method 3: Look for barcode in product images (basic text extraction)
                if not product['Barcode (EAN/UPC)']:
                    for img_url in product['Product Images']:
                        if 'barcode' in img_url.lower() or 'code' in img_url.lower():
                            # This would require image processing to extract barcode from image
                            # For now, we'll just note that barcode might be in image
                            product['Barcode (EAN/UPC)'] = 'See product image'
                            break
                
                # Method 4: Look for barcode in structured data
                if not product['Barcode (EAN/UPC)']:
                    # Look for JSON-LD structured data
                    json_scripts = soup.find_all('script', type='application/ld+json')
                    for script in json_scripts:
                        try:
                            import json
                            data = json.loads(script.string)
                            if isinstance(data, dict):
                                if 'gtin' in data:
                                    product['Barcode (EAN/UPC)'] = str(data['gtin'])
                                    break
                                elif 'sku' in data:
                                    product['Barcode (EAN/UPC)'] = str(data['sku'])
                                    break
                        except:
                            continue
                            
            except Exception as e:
                print(f"Error extracting barcode: {e}")
                pass
            
            # Debug: Print what we actually extracted
            print(f"Successfully scraped: {product['Product Name']}")
            print(f"  Brand: {product['Brand Name']}")
            print(f"  Price: {product['Price']}")
            print(f"  Size: {product['Size/Volume']}")
            print(f"  Barcode: {product['Barcode (EAN/UPC)']}")
            print(f"  Ingredients: {product['Ingredients'][:50]}..." if product['Ingredients'] else "  Ingredients: None")
            return product
            
        except Exception as e:
            print(f"Error extracting product data: {e}")
            return product

    def extract_product_id(self, url):
        """Extract product ID from URL"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.split('/')
            for part in reversed(path_parts):
                if part and part not in ['product', 'products', 'p']:
                    return part
            return parsed.path.split('/')[-1] or f"id_{hash(url)}"
        except:
            return f"id_{hash(url)}"

    def scrape_products(self, min_products=10):
        """Main method to scrape products"""
        product_urls = self.get_product_urls()
        print(f"Found {len(product_urls)} product URLs")
        
        # Scrape each product
        for i, url in enumerate(product_urls[:min_products]):
            print(f"Scraping product {i+1}/{min_products}")
            product_data = self.extract_product_data(url)
            if product_data['Product Name']:
                self.product_data.append(product_data)
            time.sleep(random.uniform(2, 4))
        
        print(f"Successfully scraped {len(self.product_data)} products")

    def save_to_excel(self, filename="twcm_skincare_products.xlsx"):
        """Save data to Excel file"""
        if not self.product_data:
            print("No data to save")
            return
            
        df = pd.DataFrame(self.product_data)
        
        # Ensure all required columns exist
        expected_columns = [
            'Product ID', 'Product Name', 'Product Line Name', 'Brand Name', 
            'Product Description', 'Product Images', 'Barcode (EAN/UPC)', 
            'Price', 'Size/Volume', 'Ingredients', 'Skin Concern', 'Source URL'
        ]
        
        for col in expected_columns:
            if col not in df.columns:
                df[col] = ''
        
        # Reorder columns
        df = df[expected_columns]
        
        # Save to Excel
        try:
            filepath = os.path.join(os.getcwd(), filename)
            df.to_excel(filepath, index=False)
            print(f"Data saved to {filepath}")
        except Exception as e:
            print(f"Error saving Excel file: {e}")
        
    def save_to_json(self, filename="twcm_skincare_products.json"):
        """Save data to JSON file"""
        if not self.product_data:
            print("No data to save")
            return
            
        try:
            filepath = os.path.join(os.getcwd(), filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.product_data, f, indent=2, ensure_ascii=False)
            print(f"Data saved to {filepath}")
        except Exception as e:
            print(f"Error saving JSON file: {e}")
        
    def close(self):
        """Close the browser"""
        self.driver.quit()

# Main execution
if __name__ == "__main__":
    print("Starting Terry White Chemmart scraper...")
    
    try:
        scraper = TWCMScraper(headless=False)
        scraper.scrape_products(min_products=10)
        scraper.save_to_excel()
        scraper.save_to_json()
        scraper.close()
        print("Scraping completed successfully!")
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        print("Please make sure ChromeDriver is properly installed and accessible.")