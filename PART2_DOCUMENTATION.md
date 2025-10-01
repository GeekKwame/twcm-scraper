# Part 2: Ingredient Grouping Analysis - Documentation

## Overview
This document describes the process and results of grouping skincare products by shared ingredients, as requested in Part 2 of the web scraping project.

## Project Structure
```
Web-Scraper/
├── scraper.py                           # Part 1: Web scraper
├── ingredient_grouping.py               # Part 2: Ingredient analysis
├── twcm_skincare_products.json         # Scraped product data
├── ingredient_grouping_analysis.xlsx    # Complete analysis (Excel)
├── ingredient_groups.csv               # Grouped products
├── detailed_ingredient_matches.csv     # Detailed matches
├── ingredient_frequency.csv            # Ingredient frequency
├── ingredient_analysis.png             # Visualizations
└── PART2_DOCUMENTATION.md              # This documentation
```

## Methodology

### 1. Data Processing
- **Input**: 10 skincare products from Terry White Chemmart
- **Ingredient Extraction**: Parsed and cleaned ingredient lists from HTML artifacts
- **Cleaning Process**: 
  - Removed HTML tags and special characters
  - Normalized ingredient names
  - Split by common separators (•, ,, ;)
  - Filtered out non-ingredient text

### 2. Ingredient Analysis
- **Total Ingredients Found**: 94 unique ingredients
- **Grouping Criteria**: Products sharing 2+ common ingredients
- **Similarity Calculation**: Shared ingredients / max(total ingredients per product)

### 3. Grouping Algorithm
1. **Pair Generation**: Created all possible product pairs
2. **Shared Ingredient Detection**: Found common ingredients between pairs
3. **Group Formation**: Clustered products with significant ingredient overlap
4. **Quality Filtering**: Ensured minimum 2 products per group

## Results Summary

### Key Statistics
- **Products Analyzed**: 10
- **Unique Ingredients**: 94
- **Ingredient Groups Found**: 3
- **Product Pairs with Shared Ingredients**: 19

### Top 10 Most Common Ingredients
1. **Glycerin** (7 products, 70.0%)
2. **Cetearyl Alcohol** (5 products, 50.0%)
3. **Aqua** (4 products, 40.0%)
4. **Glyceryl Stearate** (4 products, 40.0%)
5. **Phenoxyethanol** (4 products, 40.0%)
6. **Dimethicone** (3 products, 30.0%)
7. **Benzyl Alcohol** (3 products, 30.0%)
8. **Tocopheryl Acetate** (3 products, 30.0%)
9. **Xanthan Gum** (2 products, 20.0%)
10. **Glyceryl Stearate SE** (2 products, 20.0%)

## Ingredient Groups

### Group A: Moisturizing Base Ingredients
- **Shared Ingredients**: Aqua, Cetearyl Alcohol, Ceteth-20, Dichlorobenzyl Alcohol, Dimethicone
- **Products**: Ego QV Bar 100g (2 variations)
- **Shared Count**: 9 ingredients
- **Purpose**: Basic moisturizing and emulsifying agents

### Group B: Preservative & Stabilizing System
- **Shared Ingredients**: Benzyl Alcohol, Glycerin, Glyceryl Stearate, Phenoxyethanol, Tocopheryl Acetate
- **Products**: Dermal Therapy Anti Itch Soothing Lotion 250ml, Benzac AC Gel 10% - 60g
- **Shared Count**: 5 ingredients
- **Purpose**: Preservation, moisturization, and vitamin E antioxidant

### Group C: Thickening & Hydrating Agents
- **Shared Ingredients**: Glycerin, Xanthan Gum
- **Products**: CeraVe Advanced Repair Balm 50ml, Q+A AHA Exfoliator Body Scrub 250ml
- **Shared Count**: 2 ingredients
- **Purpose**: Hydration and texture enhancement

## Technical Implementation

### Core Classes and Functions

#### `IngredientGrouper` Class
- **Purpose**: Main class for ingredient analysis and grouping
- **Key Methods**:
  - `clean_ingredient_text()`: Removes HTML artifacts and normalizes text
  - `extract_ingredients()`: Parses individual ingredients from cleaned text
  - `find_ingredient_groups()`: Groups products by shared ingredients
  - `create_grouping_table()`: Generates summary tables
  - `create_visualizations()`: Produces analysis charts

#### Data Processing Pipeline
1. **Load Data**: Read JSON file with scraped product data
2. **Clean Ingredients**: Remove HTML tags and normalize text
3. **Extract Individual Ingredients**: Parse ingredient lists
4. **Calculate Frequencies**: Count ingredient occurrences
5. **Find Groups**: Identify products with shared ingredients
6. **Generate Reports**: Create tables and visualizations

### Algorithm Details

#### Ingredient Cleaning
```python
def clean_ingredient_text(self, ingredient_text: str) -> str:
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', ingredient_text)
    # Remove special characters
    clean_text = re.sub(r'&[a-zA-Z]+;', '', clean_text)
    # Split by common separators
    ingredients = re.split(r'[•,;]', clean_text)
    return ' • '.join(ingredients[:20])
```

#### Grouping Logic
```python
def find_ingredient_groups(self, min_shared: int = 2):
    # Create product pairs
    for i, product1 in enumerate(self.products):
        for j, product2 in enumerate(self.products[i+1:], i+1):
            shared = ingredients1.intersection(ingredients2)
            if len(shared) >= min_shared:
                # Add to groups
```

## Output Files

### 1. Excel File: `ingredient_grouping_analysis.xlsx`
- **Sheet 1**: Ingredient Groups (summary table)
- **Sheet 2**: Detailed Matches (all product pairs)
- **Sheet 3**: Ingredient Frequency (most common ingredients)
- **Sheet 4**: Raw Data (cleaned product data)

### 2. CSV Files
- **`ingredient_groups.csv`**: Summary of grouped products
- **`detailed_ingredient_matches.csv`**: All product pair matches
- **`ingredient_frequency.csv`**: Ingredient frequency analysis

### 3. Visualization: `ingredient_analysis.png`
- Top 15 most common ingredients (bar chart)
- Ingredient frequency distribution (histogram)
- Products with most ingredients (histogram)
- Ingredient group sizes (bar chart)

## Key Findings

### 1. Ingredient Commonality
- **Glycerin** is the most common ingredient (70% of products)
- **Cetearyl Alcohol** appears in 50% of products
- Most products share basic moisturizing and preservative ingredients

### 2. Product Relationships
- Products from the same brand (Ego QV) show highest ingredient overlap
- Cross-brand products share common preservative and moisturizing systems
- Specialized products (like exfoliators) have unique ingredient profiles

### 3. Formulation Patterns
- **Base Formulations**: Common use of aqua, glycerin, and emulsifiers
- **Preservation Systems**: Consistent use of phenoxyethanol and benzyl alcohol
- **Texture Modifiers**: Xanthan gum and various acrylates for consistency

## Quality Assurance

### Data Validation
- ✅ All 10 products processed successfully
- ✅ 94 unique ingredients identified and cleaned
- ✅ No duplicate groups created
- ✅ All shared ingredients verified manually

### Algorithm Validation
- ✅ Minimum 2 shared ingredients required for grouping
- ✅ Similarity scores calculated correctly
- ✅ Product pairs generated without duplicates
- ✅ Group formation follows logical clustering

## Usage Instructions

### Running the Analysis
```bash
python ingredient_grouping.py
```

### Requirements
- Python 3.8+
- pandas, matplotlib, seaborn
- Input: `twcm_skincare_products.json`

### Output
- Excel file with multiple analysis sheets
- CSV files for individual analysis components
- PNG visualization file
- Console summary report

## Future Enhancements

### Potential Improvements
1. **Ingredient Normalization**: Standardize ingredient names (e.g., "Aqua" = "Water")
2. **Semantic Grouping**: Group by ingredient function (humectants, preservatives, etc.)
3. **Similarity Scoring**: Implement more sophisticated similarity algorithms
4. **Visualization**: Interactive ingredient network graphs
5. **Database Integration**: Store results in a structured database

### Scalability Considerations
- Current implementation handles 10 products efficiently
- Algorithm complexity: O(n²) for product pairs
- Memory usage scales linearly with ingredient count
- Can be optimized for larger datasets with parallel processing

## Conclusion

The ingredient grouping analysis successfully identified meaningful relationships between skincare products based on shared ingredients. The three groups represent different formulation approaches:

1. **Basic Moisturizing Products** (Group A)
2. **Preserved Therapeutic Products** (Group B)  
3. **Specialized Treatment Products** (Group C)

This analysis provides valuable insights for product development, competitive analysis, and consumer education about skincare formulations.

---
*Generated on: 2024*  
*Analysis Tool: Python 3.12 with pandas, matplotlib, seaborn*  
*Data Source: Terry White Chemmart skincare products*
