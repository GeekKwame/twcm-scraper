#!/usr/bin/env python3
"""
Part 2: Group Products with Matching Key Ingredients

This script analyzes scraped skincare product data and groups products
that share 2-3+ common ingredients.

"""

import json
import pandas as pd
import re
from collections import defaultdict, Counter
from itertools import combinations
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Set, Tuple
import warnings
warnings.filterwarnings('ignore')

class IngredientGrouper:
    """Class to group skincare products by shared ingredients."""
    
    def __init__(self, json_file_path: str):
        """Initialize with scraped product data."""
        self.json_file_path = json_file_path
        self.products = []
        self.ingredient_groups = defaultdict(list)
        self.ingredient_frequency = Counter()
        self.cleaned_ingredients = {}
        
    def load_data(self):
        """Load product data from JSON file."""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                self.products = json.load(f)
            print(f"✅ Loaded {len(self.products)} products from {self.json_file_path}")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
        return True
    
    def clean_ingredient_text(self, ingredient_text: str) -> str:
        """Clean and extract ingredient list from messy text."""
        if not ingredient_text or ingredient_text.strip() == "":
            return ""
        
        # Remove HTML tags and artifacts
        clean_text = re.sub(r'<[^>]+>', '', ingredient_text)
        clean_text = re.sub(r'&[a-zA-Z]+;', '', clean_text)
        clean_text = re.sub(r'[^\w\s\.,;•/()-]', '', clean_text)
        
        # Look for ingredient patterns
        ingredient_patterns = [
            r'INGREDIENTS[:\s]*([^•]+)',
            r'Ingredients[:\s]*([^•]+)',
            r'([A-Z][A-Z\s]+/[A-Z\s]+[^•]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+[^•]+)',
            r'([A-Z][a-z]+[^•]+)'
        ]
        
        ingredients = []
        for pattern in ingredient_patterns:
            matches = re.findall(pattern, clean_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                # Split by common separators
                parts = re.split(r'[•,;]', match)
                for part in parts:
                    part = part.strip()
                    if len(part) > 2 and not part.lower().startswith(('ingredients', 'contains', 'made')):
                        ingredients.append(part)
        
        # If no patterns found, try splitting by common separators
        if not ingredients:
            parts = re.split(r'[•,;]', clean_text)
            for part in parts:
                part = part.strip()
                if len(part) > 2 and not part.lower().startswith(('ingredients', 'contains', 'made')):
                    ingredients.append(part)
        
        return ' • '.join(ingredients[:20])  # Limit to first 20 ingredients
    
    def extract_ingredients(self, ingredient_text: str) -> Set[str]:
        """Extract individual ingredients from cleaned text."""
        if not ingredient_text:
            return set()
        
        # Split by common separators
        ingredients = re.split(r'[•,;]', ingredient_text)
        cleaned_ingredients = set()
        
        for ingredient in ingredients:
            ingredient = ingredient.strip()
            if len(ingredient) > 2:
                # Clean up ingredient name
                ingredient = re.sub(r'\([^)]*\)', '', ingredient)  # Remove parentheses
                ingredient = re.sub(r'\s+', ' ', ingredient)  # Normalize whitespace
                ingredient = ingredient.strip()
                
                if len(ingredient) > 2 and not ingredient.lower().startswith(('ingredients', 'contains', 'made')):
                    cleaned_ingredients.add(ingredient.lower())
        
        return cleaned_ingredients
    
    def process_ingredients(self):
        """Process all product ingredients and create frequency counts."""
        print("🔍 Processing ingredient data...")
        
        for product in self.products:
            product_id = product.get('Product ID', '')
            product_name = product.get('Product Name', '')
            ingredient_text = product.get('Ingredients', '')
            
            # Clean ingredient text
            cleaned_text = self.clean_ingredient_text(ingredient_text)
            self.cleaned_ingredients[product_id] = cleaned_text
            
            # Extract individual ingredients
            ingredients = self.extract_ingredients(cleaned_text)
            
            # Update frequency counter
            for ingredient in ingredients:
                self.ingredient_frequency[ingredient] += 1
            
            # Store ingredients for this product
            product['cleaned_ingredients'] = ingredients
            product['cleaned_ingredient_text'] = cleaned_text
        
        print(f"✅ Processed ingredients for {len(self.products)} products")
        print(f"📊 Found {len(self.ingredient_frequency)} unique ingredients")
    
    def find_ingredient_groups(self, min_shared: int = 2, min_products: int = 2):
        """Find groups of products that share common ingredients."""
        print(f"🔍 Finding groups with {min_shared}+ shared ingredients...")
        
        # Create product pairs and find shared ingredients
        product_pairs = []
        
        for i, product1 in enumerate(self.products):
            for j, product2 in enumerate(self.products[i+1:], i+1):
                ingredients1 = product1.get('cleaned_ingredients', set())
                ingredients2 = product2.get('cleaned_ingredients', set())
                
                if len(ingredients1) == 0 or len(ingredients2) == 0:
                    continue
                
                shared = ingredients1.intersection(ingredients2)
                if len(shared) >= min_shared:
                    product_pairs.append({
                        'product1_id': product1.get('Product ID', ''),
                        'product1_name': product1.get('Product Name', ''),
                        'product2_id': product2.get('Product ID', ''),
                        'product2_name': product2.get('Product Name', ''),
                        'shared_ingredients': list(shared),
                        'shared_count': len(shared),
                        'ingredients1_count': len(ingredients1),
                        'ingredients2_count': len(ingredients2)
                    })
        
        # Group products by shared ingredients
        groups = defaultdict(list)
        used_products = set()
        
        # Sort pairs by number of shared ingredients (descending)
        product_pairs.sort(key=lambda x: x['shared_count'], reverse=True)
        
        for pair in product_pairs:
            p1_id = pair['product1_id']
            p2_id = pair['product2_id']
            
            # Skip if either product is already in a group
            if p1_id in used_products or p2_id in used_products:
                continue
            
            # Create a new group
            group_key = tuple(sorted(pair['shared_ingredients']))
            groups[group_key].extend([p1_id, p2_id])
            used_products.update([p1_id, p2_id])
        
        # Filter groups by minimum product count
        filtered_groups = {k: v for k, v in groups.items() if len(set(v)) >= min_products}
        
        self.ingredient_groups = filtered_groups
        print(f"✅ Found {len(filtered_groups)} ingredient groups")
        
        return product_pairs, filtered_groups
    
    def create_grouping_table(self, product_pairs: List[Dict], groups: Dict) -> pd.DataFrame:
        """Create a table showing product groupings by shared ingredients."""
        grouping_data = []
        
        for group_idx, (shared_ingredients, product_ids) in enumerate(groups.items(), 1):
            # Get product names for this group
            product_names = []
            for product in self.products:
                if product.get('Product ID') in product_ids:
                    product_names.append(product.get('Product Name', ''))
            
            # Get most common ingredients in this group
            common_ingredients = list(shared_ingredients)[:5]  # Top 5 shared ingredients
            
            grouping_data.append({
                'Group': f'Group {chr(64 + group_idx)}',  # A, B, C, etc.
                'Shared_Ingredients': ', '.join(common_ingredients),
                'Product_Names': ' | '.join(product_names),
                'Product_Count': len(set(product_ids)),
                'Shared_Count': len(shared_ingredients)
            })
        
        return pd.DataFrame(grouping_data)
    
    def create_detailed_analysis(self, product_pairs: List[Dict]) -> pd.DataFrame:
        """Create detailed analysis of ingredient matches."""
        detailed_data = []
        
        for pair in product_pairs:
            detailed_data.append({
                'Product_1': pair['product1_name'],
                'Product_2': pair['product2_name'],
                'Shared_Ingredients': ', '.join(pair['shared_ingredients'][:5]),
                'Shared_Count': pair['shared_count'],
                'Total_Ingredients_1': pair['ingredients1_count'],
                'Total_Ingredients_2': pair['ingredients2_count'],
                'Similarity_Score': pair['shared_count'] / max(pair['ingredients1_count'], pair['ingredients2_count'])
            })
        
        return pd.DataFrame(detailed_data)
    
    def create_ingredient_frequency_analysis(self) -> pd.DataFrame:
        """Create analysis of most common ingredients."""
        # Get top ingredients
        top_ingredients = self.ingredient_frequency.most_common(20)
        
        frequency_data = []
        for ingredient, count in top_ingredients:
            frequency_data.append({
                'Ingredient': ingredient.title(),
                'Frequency': count,
                'Percentage': (count / len(self.products)) * 100
            })
        
        return pd.DataFrame(frequency_data)
    
    def create_visualizations(self):
        """Create visualizations for ingredient analysis."""
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Skincare Product Ingredient Analysis', fontsize=16, fontweight='bold')
        
        # 1. Top 15 Most Common Ingredients
        top_15 = self.ingredient_frequency.most_common(15)
        ingredients, counts = zip(*top_15)
        
        axes[0, 0].barh(range(len(ingredients)), counts)
        axes[0, 0].set_yticks(range(len(ingredients)))
        axes[0, 0].set_yticklabels([ing.title() for ing in ingredients])
        axes[0, 0].set_xlabel('Frequency')
        axes[0, 0].set_title('Top 15 Most Common Ingredients')
        axes[0, 0].invert_yaxis()
        
        # 2. Ingredient Frequency Distribution
        frequency_counts = Counter(self.ingredient_frequency.values())
        axes[0, 1].bar(frequency_counts.keys(), frequency_counts.values())
        axes[0, 1].set_xlabel('Number of Products')
        axes[0, 1].set_ylabel('Number of Ingredients')
        axes[0, 1].set_title('Ingredient Frequency Distribution')
        
        # 3. Products with Most Ingredients
        product_ingredient_counts = []
        for product in self.products:
            count = len(product.get('cleaned_ingredients', set()))
            if count > 0:
                product_ingredient_counts.append(count)
        
        axes[1, 0].hist(product_ingredient_counts, bins=10, alpha=0.7, color='skyblue')
        axes[1, 0].set_xlabel('Number of Ingredients per Product')
        axes[1, 0].set_ylabel('Number of Products')
        axes[1, 0].set_title('Distribution of Ingredients per Product')
        
        # 4. Ingredient Group Sizes
        if self.ingredient_groups:
            group_sizes = [len(set(products)) for products in self.ingredient_groups.values()]
            axes[1, 1].bar(range(1, len(group_sizes) + 1), group_sizes, color='lightcoral')
            axes[1, 1].set_xlabel('Group Number')
            axes[1, 1].set_ylabel('Number of Products in Group')
            axes[1, 1].set_title('Ingredient Group Sizes')
        else:
            axes[1, 1].text(0.5, 0.5, 'No ingredient groups found', 
                           ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Ingredient Group Sizes')
        
        plt.tight_layout()
        plt.savefig('ingredient_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def save_results(self, grouping_table: pd.DataFrame, detailed_analysis: pd.DataFrame, 
                    frequency_analysis: pd.DataFrame):
        """Save all results to Excel and CSV files."""
        print("💾 Saving results...")
        
        # Save to Excel with multiple sheets
        with pd.ExcelWriter('ingredient_grouping_analysis.xlsx', engine='openpyxl') as writer:
            grouping_table.to_excel(writer, sheet_name='Ingredient_Groups', index=False)
            detailed_analysis.to_excel(writer, sheet_name='Detailed_Matches', index=False)
            frequency_analysis.to_excel(writer, sheet_name='Ingredient_Frequency', index=False)
            
            # Add raw data sheet
            raw_data = []
            for product in self.products:
                raw_data.append({
                    'Product_ID': product.get('Product ID', ''),
                    'Product_Name': product.get('Product Name', ''),
                    'Brand_Name': product.get('Brand Name', ''),
                    'Cleaned_Ingredients': product.get('cleaned_ingredient_text', ''),
                    'Ingredient_Count': len(product.get('cleaned_ingredients', set()))
                })
            
            pd.DataFrame(raw_data).to_excel(writer, sheet_name='Raw_Data', index=False)
        
        # Save individual CSV files
        grouping_table.to_csv('ingredient_groups.csv', index=False)
        detailed_analysis.to_csv('detailed_ingredient_matches.csv', index=False)
        frequency_analysis.to_csv('ingredient_frequency.csv', index=False)
        
        print("✅ Results saved to:")
        print("   - ingredient_grouping_analysis.xlsx")
        print("   - ingredient_groups.csv")
        print("   - detailed_ingredient_matches.csv")
        print("   - ingredient_frequency.csv")
        print("   - ingredient_analysis.png")
    
    def print_summary(self, grouping_table: pd.DataFrame, detailed_analysis: pd.DataFrame):
        """Print a summary of the analysis."""
        print("\n" + "="*60)
        print("📊 INGREDIENT GROUPING ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"\n🔢 Total Products Analyzed: {len(self.products)}")
        print(f"🧪 Total Unique Ingredients: {len(self.ingredient_frequency)}")
        print(f"👥 Ingredient Groups Found: {len(grouping_table)}")
        print(f"🔗 Product Pairs with Shared Ingredients: {len(detailed_analysis)}")
        
        print(f"\n📈 Top 10 Most Common Ingredients:")
        for i, (ingredient, count) in enumerate(self.ingredient_frequency.most_common(10), 1):
            percentage = (count / len(self.products)) * 100
            print(f"   {i:2d}. {ingredient.title():<25} ({count:2d} products, {percentage:5.1f}%)")
        
        if not grouping_table.empty:
            print(f"\n👥 Ingredient Groups:")
            for _, row in grouping_table.iterrows():
                print(f"   {row['Group']}: {row['Product_Count']} products")
                print(f"      Shared: {row['Shared_Ingredients'][:80]}...")
                print(f"      Products: {row['Product_Names'][:80]}...")
                print()
        
        print("="*60)

def main():
    """Main function to run the ingredient grouping analysis."""
    print("🚀 Starting Part 2: Ingredient Grouping Analysis")
    print("="*60)
    
    # Initialize the grouper
    grouper = IngredientGrouper('twcm_skincare_products.json')
    
    # Load and process data
    if not grouper.load_data():
        return
    
    grouper.process_ingredients()
    
    # Find ingredient groups (minimum 2 shared ingredients, minimum 2 products per group)
    product_pairs, groups = grouper.find_ingredient_groups(min_shared=2, min_products=2)
    
    # Create analysis tables
    grouping_table = grouper.create_grouping_table(product_pairs, groups)
    detailed_analysis = grouper.create_detailed_analysis(product_pairs)
    frequency_analysis = grouper.create_ingredient_frequency_analysis()
    
    # Create visualizations
    grouper.create_visualizations()
    
    # Save results
    grouper.save_results(grouping_table, detailed_analysis, frequency_analysis)
    
    # Print summary
    grouper.print_summary(grouping_table, detailed_analysis)
    
    print("\n✅ Analysis complete! Check the generated files for detailed results.")

if __name__ == "__main__":
    main()
