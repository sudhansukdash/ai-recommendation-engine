#Use the ai-recommendation-engine as project root folder as links are all relative to that
#Creating the item-user matrix from interactions_final.csv using pandas

import pandas as pd
import os
from sklearn.preprocessing import normalize #To debiase the popularity bias created

#Return the project root folder name
PROJECT_ROOT = os.path.basename(os.getcwd())

print("\nCreating user-item matrix...")

#Reading the interactions_final.csv and storing it on a DataFrame
interactions = pd.read_csv("data/processed/interactions_final.csv")

#Converting the user_id and pr_id as rows and cols respectively and total_scores as cell values using pandas pivot 
grouped_interactions = interactions.pivot(index="user_id", columns="pr_id", values="total_scores")
grouped_interactions = grouped_interactions.fillna(0)
grouped_interactions = grouped_interactions.astype(float)

#So when we are using popularity bias most of the users have interacted with the same product, so that popular product comes up in all users recommendations, these items act like "magnets"—they appear in everyone's history, so everyone looks "similar" just because they all bought milk or a generic t-shirt.
print("Normalizing interaction scores...")

# Using normalise l2(euclidean length) and as we are using item based CF so axis=0 mean, recommend based on similar products as products are the columns. The normalization l2 just finds the ratio of each scores about its length and gives a value 0-1, based on that similar values across users are considered similar products.
matrix_values = normalize(grouped_interactions.values, norm='l2', axis=0)

# Rows = Items, Columns = Users (Transposed for Item-Based CF)
item_user_matrix = pd.DataFrame(
    matrix_values,
    index=grouped_interactions.index, 
    columns=grouped_interactions.columns
).T

print("Item-user matrix created successfully!")
print(f"Products, Users: {item_user_matrix.shape}")

#Saving the user-item matrix dataframe as .csv file
#In this user_item matrix the user_id is the index itself -> pivot (item CF based) 
item_user_matrix.to_csv("data/processed/item_user_matrix.csv")

print(f"File saved as item_user_matrix.csv under {PROJECT_ROOT}/data/processed")