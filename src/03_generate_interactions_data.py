#Creating interactions taking user data and product data from raw csv files
import random
import pandas as pd

#Reads users and product data from csv and store it in form of DataFrame
users = pd.read_csv("../ai-recommendation-engine/data/raw/users_raw.csv") 
products = pd.read_csv("../ai-recommendation-engine/data/raw/products_raw.csv")

#Reading only the user_id from the dataframe->users, and converting it to a list
user_ids = users["user_id"].to_list()

#Reading only the product_id from the dataframe->products, and converting it to a list
product_ids = products["pr_id"].to_list()

interactions = []

#Creating a list ambigious interactions consisting of 4 unique interaction types: view, cart, wishlist, purchase
interactions_type = ["view","View","VIEW","Cart ","cart","Wishlist ","WISHLIST","wishlist","purchase","Purchase "]

#Creating 600 interactions data
for i in range(600):
    
    interactions_data = {

        "user_id" : random.choice(user_ids),
        "pr_id" : random.choice(product_ids),
        "interactions_type": random.choice(interactions_type)
    }
    interactions.append(interactions_data)

#Converting list of dictionaries to dataframes and storing it in df
df = pd.DataFrame(interactions)

#Converting dataframe to .csv file
df.to_csv("../ai-recommendation-engine/data/raw/interactions_raw.csv",index=False)

#Success message 
print("Interaction data generated successfully!!!")