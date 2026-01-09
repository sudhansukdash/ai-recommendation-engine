#Use the ai-recommendation-engine as project root folder as links are all relative to that
#Creating interactions taking user data and product data from raw csv files
import random
import pandas as pd

print("Starting Interaction data generation...")
#Reads users and product data from csv and store it in form of DataFrame
users = pd.read_csv("../ai-recommendation-engine/data/raw/users_raw.csv") 
products = pd.read_csv("../ai-recommendation-engine/data/raw/products_raw.csv")

#Reading only the user_id from the dataframe->users, and converting it to a list
user_ids = users["user_id"].to_list()

#Reading only the product_id from the dataframe->products, and converting it to a list
product_ids = products["pr_id"].to_list()

interactions = []

#Creating a list ambigious interactions consisting of 4 unique interaction types: view, cart, wishlist, purchase
interaction_type = ["view","View","VIEW","Cart ","cart","Wishlist ","WISHLIST","wishlist","purchase","Purchase ",None]

#Creating 600 interactions data
for i in range(16000):
    
    interactions_data = {

        "user_id" : random.choice(user_ids),
        "pr_id" : random.choice(product_ids),
        "interaction_type" : random.choice(interaction_type)
    }
    interactions.append(interactions_data)

#Converting list of dictionaries to dataframes and storing it in df
df = pd.DataFrame(interactions)
print("Interaction data generation success!")

#Converting dataframe to .csv file
df.to_csv("../ai-recommendation-engine/data/raw/interactions_raw.csv",index=False)

print("File saved as interactions_raw.csv under ai-recommendation-engine/data/raw/")