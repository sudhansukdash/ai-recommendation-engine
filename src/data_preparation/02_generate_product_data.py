#Use the ai-recommendation-engine as project root folder as links are all relative to that
#To generate synthetic product pr_data and converting it into csv file
import random, pandas as pd
import os

#Return the project root folder name
PROJECT_ROOT = os.path.basename(os.getcwd())

#Allows to create same random generations even if we execute the file 100 times, essential as this file is linked with product images that are stored in data/
random.seed(42)

products = []

print("\nStarting product data generation...")

#Splitted entire category into sub-groups, to improve the description and also full names of products such that they are more accurate than before, each category is divided into two groups with related items and adj and var that work together and make sense
#This improves the semantic consistencies of descriptions and names
category_subgroups = {
    "electronics": [
        # Group 1: Computers & Phones
        {
            "base": ["Laptop", "Smartphone", "Tablet", "Monitor"],
            "adj": ["Pro", "Gaming", "Ultra", "High-Performance", "Fast", "Slim"],
            "var": ["2025 Edition", "Max", "Pro-Max", "Gen-2", "Fold", "Lite"],
            "search_terms": "futuristic technology", #terms used for image generations by ai
            "templates": [
                "Experience the power of this {adj} {base}. Designed with {var} specs.",
                "The {var} {base} defines {adj} excellence. Perfect for high-end tasks."
            ]
        },
        # Group 2: Accessories
        {
            "base": ["Headphones", "Smartwatch", "Speaker", "Camera", "Mouse", "Keyboard"],
            "adj": ["Wireless", "Noise-Cancelling", "Compact", "Smart", "Bluetooth", "Ergonomic"],
            "var": ["Black", "Silver", "Mini", "Sport Edition", "Bass Boost", "RGB"],
            "search_terms": "electronic gadget",
            "templates": [
                "Upgrade your setup with this {adj} {base}. Features a {var} finish.",
                "Get the best in class {base}. This {adj} model comes in {var} style."
            ]
        }
    ],
    
    "fashion": [
        # Group 1: Clothing (Fabric based)
        {
            "base": ["T-Shirt", "Jeans", "Jacket", "Kurta", "Saree", "Suit"],
            "adj": ["Cotton", "Slim-Fit", "Designer", "Casual", "Formal", "Summer", "Silk", "Printed"],
            "var": ["Small", "Medium", "Large", "Red", "Blue", "Black"],
            "search_terms": "clothing fashion model",
            "templates": [
                "Upgrade your wardrobe with this {adj} {base}. The {var} size fits perfectly.",
                "Stay trendy with our {adj} {base}. A classic choice in {var}."
            ]
        },
        # Group 2: Accessories (Leather/Metal based)
        {
            "base": ["Sneakers", "Watch", "Handbag", "Sunglasses", "Heels"],
            "adj": ["Leather", "Classic", "Vintage", "Stylish", "Premium", "Waterproof"],
            "var": ["Brown", "Black", "Tan", "Sport", "Luxury Edition"],
            "search_terms": "fashion accessory",
            "templates": [
                "Complete your look with this {adj} {base}. Comes in a stunning {var} color.",
                "This {adj} {base} is perfect for any occasion. Features {var} details."
            ]
        }
    ],
    
    "grocery": [
        # Group 1: Staples (Weight based)
        {
            "base": ["Rice", "Wheat", "Sugar", "Dal"],
            "adj": ["Organic", "Premium", "Whole", "Polished", "Refined"],
            "var": ["1kg", "5kg", "10kg", "Bag", "Sack"],
            "search_terms": "grain food sack",
            "templates": ["Quality {adj} {base} for your daily meals. Comes in a {var} pack."]
        },
        # Group 2: Packaged Goods (Count/Flavor based)
        {
            "base": ["Oil", "Spices", "Coffee", "Tea", "Biscuits", "Chips"],
            "adj": ["Fresh", "Tasty", "Crunchy", "Pure", "Aromatic", "Spicy"],
            "var": ["Pack of 3", "Jar", "Box", "Pouch", "Instant", "Family Pack"],
            "search_terms": "supermarket packaged food",
            "templates": ["Enjoy the taste of {adj} {base}. The {var} is great for sharing."]
        }
    ],
    
    "daily_essential": [
        # Group 1: Personal Care
        {
            "base": ["Toothpaste", "Soap", "Shampoo", "Face Wash", "Sanitizer"],
            "adj": ["Antibacterial", "Herbal", "Refreshing", "Cool", "Gentle"],
            "var": ["Pack of 2", "Large", "Lemon", "Neem", "Aloe Vera", "Mint"],
            "search_terms": "bathroom hygiene product",
            "templates": ["Keep it fresh with our {adj} {base}. Enriched with {var}."]
        },
        # Group 2: Home Care
        {
            "base": ["Detergent", "Towel", "Mask", "Tissue", "Cleaner"],
            "adj": ["Strong", "Soft", "Clean", "Daily", "Hygenic"],
            "var": ["1L", "500ml", "Box", "Roll", "Active"],
            "search_terms": "cleaning product household",
            "templates": ["Essential {base} for your home. This {adj} version comes in {var}."]
        }
    ],

    "luxury": [
        # Group 1: Jewelry (Gold/Diamond)
        {
            "base": ["Diamond Ring", "Gold Necklace", "Bracelet", "Earrings"],
            "adj": ["Imported", "Handcrafted", "Genuine", "Pure Gold", "Exclusive"],
            "var": ["18k", "24k", "Platinum", "Diamond", "Ruby", "Sapphire"],
            "search_terms": "expensive jewelry gold",
            "templates": ["The ultimate symbol of elegance: {adj} {base} with {var} setting."]
        },
        # Group 2: High-End Fashion (Leather/Silk)
        {
            "base": ["Leather Bag", "Perfume", "Silk Saree", "Luxury Watch", "Clutch", "Suit"],
            "adj": ["Royal", "Elegant", "Italian", "Rare", "Limited Edition"],
            "var": ["Signature", "Custom", "Velvet Box", "Premium", "Classic"],
            "search_terms": "luxury fashion expensive",
            "templates": ["Indulge in luxury with this {adj} {base}. Comes in a {var}."]
        }
    ]
}

#Price map to map basename of products with their price more accurately 
product_price_map = {
    # Electronics
    "Laptop": (30000, 150000), "Smartphone": (10000, 80000), "Headphones": (1000, 15000),
    "Smartwatch": (2000, 25000), "Speaker": (1500, 20000), "Camera": (25000, 150000),
    "Tablet": (10000, 60000), "Monitor": (8000, 40000), "Mouse": (300, 3000), "Keyboard": (500, 5000),
    
    # Fashion
    "T-Shirt": (300, 1500), "Jeans": (800, 4000), "Jacket": (1500, 8000), "Sneakers": (1000, 10000),
    "Watch": (1000, 15000), "Handbag": (1000, 8000), "Sunglasses": (500, 5000),
    "Kurta": (500, 3000), "Saree": (1000, 15000), "Heels": (800, 5000), "Suit": (5000, 30000),
    
    # Grocery
    "Rice": (50, 500), "Wheat": (40, 200), "Oil": (100, 1500), "Spices": (50, 400),
    "Sugar": (40, 100), "Dal": (80, 200), "Coffee": (200, 1000), "Tea": (100, 800),
    "Biscuits": (20, 200), "Chips": (20, 100),
    
    # Essentials
    "Toothpaste": (50, 200), "Soap": (30, 150), "Shampoo": (100, 800), "Detergent": (100, 600),
    "Face Wash": (100, 500), "Towel": (200, 800), "Sanitizer": (50, 300), "Mask": (50, 500),
    "Tissue": (30, 200), "Cleaner": (100, 500),
    
    # Luxury
    "Diamond Ring": (20000, 200000), "Leather Bag": (5000, 50000), "Gold Necklace": (30000, 300000),
    "Perfume": (2000, 15000), "Silk Saree": (5000, 40000), "Luxury Watch": (10000, 200000),
    "Clutch": (2000, 15000), "Bracelet": (3000, 50000), "Earrings": (2000, 40000)
}

# --- ADJECTIVE MULTIPLIERS ---
#Multiplied where adj or var in list to give more accurate pricing acc. to names
price_modifiers = {
    "Pro": 1.4, "Gaming": 1.5, "Ultra": 1.3, "Max": 1.3, "Premium": 1.5, "Gold": 1.5, "Diamond": 2.0, "Royal": 1.5,
    "Lite": 0.7, "Mini": 0.8, "Compact": 0.9, "Small": 0.8, "Budget": 0.6, "Basic": 0.7
}

#Naming, casing, spacing, typos ambiguities exists in category names
dirty_category_map = {
    "electronics": ["EleCtroNicS", "elecTronIcs ", "electronics"],
    "fashion": ["FAshioN", "fashion", "Fashion"],
    "grocery": ["GROCERY", "groceries", "grocery"], 
    "daily_essential": ["Daily Essential", "daily_essential", "daily essential"],
    "luxury": ["LUXURY", "Luxury ", "luxury"]
}

# --- GENERATION LOOP ---
#Changed the loop to iterate through the Sub-Groups
total_items = 800 #How many rows to generate?
items_per_cat = int(total_items / 5) #For each category how many rows? Here 160

for cat, subgroups in category_subgroups.items():
    
    for _ in range(items_per_cat):
        
        num_p_id = random.randint(1,650)
        
        # 1. Ambiguity (50%)
        if random.random() < 0.5:
            display_cat = random.choice(dirty_category_map[cat])
        else:
            display_cat = cat

        # 2. Pick Subgroup & Generate Item
        group = random.choice(subgroups) #Two subgroups for each cat randomly choose one subgroup for each iteration
        base = random.choice(group["base"])
        adj = random.choice(group["adj"])
        var = random.choice(group["var"])
        
        # 3. Name & Description
        fname = f"{adj} {base} {var}"
        # Using the Template from the Subgroup to ensure it makes sense
        template = random.choice(group["templates"])
        
        #We use .format() to fill values inside templates because we cannot use f-strings as the var defined inside templates were not declared during definition
        final_description = template.format(adj=adj.lower(), base=base.lower(), var=var.lower())

        # 4. Price logic
        min_p, max_p = product_price_map.get(base, (100,100000)) #Fallback if product_name min max not exits in map dict use range (100,100000)
        base_cost = random.randint(min_p, max_p)
        adj_mul = price_modifiers.get(adj, 1.0)
        var_mul = price_modifiers.get(var, 1.0)
        final_cost = int(base_cost * adj_mul * var_mul)

        # 5. AI Image logic fetched from pollinations.ai
        # prompt example: "Laptop futuristic technology"
        prompt = f"{base} {group['search_terms']}"
        prompt_encoded = prompt.replace(" ", "%20")
        # seed={num_p_id} ensures consistency (P105 always looks the same)
        image_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?seed={num_p_id}&nologo=true"
        
        pr_data = {
            "pr_id" : f"P{num_p_id}",
            "pr_category" : display_cat,
            "pr_name" : fname,
            "pr_cost" : final_cost,
            "pr_image_url" : image_url,
            "pr_rating" : round(random.uniform(3.0,4.9),1),
            "pr_description" : final_description
        }
        
        products.append(pr_data)

#Converting the list of dictionaries to rows and columns using DataFrame of pandas
df = pd.DataFrame(products)

#As our for loop logic creates items by categories, ex: 160 for electronics then next category like that... so this line shuffles the row and then resets the index according to row position.
df = df.sample(frac=1).reset_index(drop=True)

print(df.info())

print("\nProduct data generation successful!")
#Convert the dataframe to csv works only if project folder is the root folder
df.to_csv("data/raw/products_raw.csv",index=False)

print(f"File saved as products_raw.csv under {PROJECT_ROOT}/data/raw/")