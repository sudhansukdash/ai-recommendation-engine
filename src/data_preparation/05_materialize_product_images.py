# Use the ai-recommendation-engine as project root folder
# This file is needed by our app so it have images to display for products, it have no contribution in recommender logic
# Logic: Read clean CSV -> Download Images -> Replace image_url with image links in local storage -> Save Final CSV
import pandas as pd
import requests #To download images from the internet using this script
import os
from tqdm import tqdm #For the loading bar during downloading images
from dotenv import load_dotenv #for loading the .env
import time

#Read the .env file
load_dotenv()

API_KEY = os.getenv("POLLINATIONS_API_KEY")

#Maintain a consistent connection to the server, instead of reconnecting after each image(increases load)
session = requests.Session()

# #Free tier (acting as a different machine for easier access)
# session.headers.update({
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
# })

# Premium version --start--
if not API_KEY:
    print("\nNo API_KEY found in .env! You may hit rate limits.")

else:
    print("\nAPI_KEY loaded successfully!")
    session.headers.update({"Authorization": f"Bearer {API_KEY}"})
# Premium version --end--

# Return the project root folder name
PROJECT_ROOT = os.path.basename(os.getcwd())

input_csv = "data/processed/products_clean.csv"   #Has online links
output_csv = "data/processed/products_final.csv"  #Has local paths
image_folder = "data/images"

#Creates a new directory in location and if it exists it ignores it.
os.makedirs(image_folder, exist_ok=True)

print(f"Starting image materialization...\nReading from: {PROJECT_ROOT}/{input_csv}\n")

#Checks if input_csv is valid or not
if not os.path.exists(input_csv):
    print("Error: Input file missing. Run 04_clean_product_data.py first.")
    exit()

df = pd.read_csv(input_csv)
print(f"Found {len(df)} products to process...")

# 2. Download Function
def download_and_get_path(row):
    # Get the URL and ID
    url = row['pr_image_url']
    p_id = row['pr_id']
    
    # --- THE RUNTIME SWAP ---
    # If you have a api key, instead of looking on public anonymous mode with limit use your private key to generate products
    if API_KEY:
        #Updating the public domain to private (for users having API_KEY)
        if "image.pollinations.ai" in url:
            # 2. Upgrade it to the VIP Door
            url = url.replace("image.pollinations.ai/prompt/", "gen.pollinations.ai/image/")
            url += "&model=seedream"
    # Define filenames
    
    filename = f"{p_id}.jpg"
    save_path = os.path.join(image_folder, filename) #Actual path in the disk
    
    # RELATIVE PATH (The one we want in the CSV for the App)
    # We force forward slashes (/) so it works on Mac/Windows/Web
    final_db_path = f"data/images/{filename}"
    
    # If file already exists locally, skip download
    if os.path.exists(save_path):
        return final_db_path
    
    # --- DOWNLOAD ---
    try:
        response = session.get(url, timeout=90)
        if response.status_code == 200:
            #Images are binary so 'wb' (write binary) is required.
            with open(save_path, 'wb') as f:
                f.write(response.content)
            time.sleep(2) #increased time.sleep to 10 for free tier else rate limit reached error
            return final_db_path
        else:
            print(f"\nFailed to download {p_id}: Status {response.status_code}-{response.text}")
            return None
    except Exception as e:
        print(f"Error downloading {p_id}: {e}")
        return None

# 3. Execution Loop
print("\nDownloading images...")

# We apply the function to every row and store results in a list new_paths
new_paths = []

#Total says the tqdm about the completion, desc says about downloading and color saying about the bar color
for index, row in tqdm(df.iterrows(), total = len(df), desc="Downloading", colour="green"):
    path = download_and_get_path(row)
    new_paths.append(path)
    
    
#Creates a new series and adds it to the df
#Works only if len(df) == len(new_paths)
df['pr_image'] = new_paths

# Remove the old URL column
if 'pr_image_url' in df.columns:
    df = df.drop(columns=['pr_image_url'])

# Drop rows where download failed
df = df.dropna(subset=['pr_image'])

# Save Final .csv file
df.to_csv(output_csv, index=False)

print(f"\nFinal products dataset stored as {PROJECT_ROOT}/{output_csv}")
print(f"Images stored in {PROJECT_ROOT}/{image_folder}")
print("Column 'pr_image_url' replaced with 'pr_image'.")