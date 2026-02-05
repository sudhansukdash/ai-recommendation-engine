#Use the ai-recommendation-engine as project root folder as links are all relative to that
#Cleaning products_raw.csv using pandas

import pandas as pd
import os
from thefuzz import process

#Return the project root folder category_name
PROJECT_ROOT = os.path.basename(os.getcwd())

print("\nStarting product data cleaning...")

#Reading the file and storing it in a variable as DataFrame
raw_products = pd.read_csv("data/raw/products_raw.csv")
clean_products = raw_products.copy()

print(clean_products.info())
# print(clean_products.value_counts(subset="pr_id", dropna=False))

# #Cleaning data by columns 

#Cleaning column: pr_id
clean_products = clean_products.drop_duplicates(subset="pr_id")
clean_products = clean_products.dropna(subset=["pr_id"])
# print(clean_products.value_counts("pr_id", dropna=False))
# print(clean_products.info())

#Cleaning column: pr_category
# print(clean_products.value_counts(subset="pr_category",dropna=False))
valid_categories = ["electronics", "fashion", "grocery", "daily_essential", "luxury"]

#function for fuzzy finder(to check typos and correct)
def fix_category(category_name):
    if pd.isna(category_name):
        return "missing"
    
    category_name = str(category_name)
    clean_category = category_name.strip().lower()

    match, score = process.extractOne(clean_category,valid_categories)
    if score >= 70:
        return match
    else:
        return "missing"
clean_products["pr_category"] = clean_products["pr_category"].apply(fix_category)
# print(clean_products.value_counts(subset="pr_category",dropna=False))

#Cleaning column: pr_name
# print(clean_products.value_counts("pr_name", dropna=False))
clean_products["pr_name"] = clean_products["pr_name"].fillna("Unknown")
# print(clean_products.value_counts("pr_name", dropna=False))

#pr_cost, pr_image_url, pr_rating is left as NaN

#Cleaning column: pr_description
clean_products["pr_description"] = clean_products["pr_description"].fillna("No description available.")

print(clean_products.info())
print("\nProduct data cleaned successfully!")

#Saving this clean_products dataframe into a new products_clean.csv file
clean_products.to_csv("data/processed/products_clean.csv", index=False)

print(f"File saved as products_clean.csv under {PROJECT_ROOT}/data/processed/")