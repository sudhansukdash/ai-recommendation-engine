#Use the ai-recommendation-engine as project root folder as links are all relative to that
#Creating the item-user matrix from interactions_final.csv using pandas

import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfTransformer #To de-bias the popularity bias

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
#TF-IDF penalizes these hyper-popular items and gives more weight to "niche" products that specific users seem to love. We are not cancelling out the entire popularity bias but the very common products to be recommended to everyone, these two steps are a common process for a synthetic data matrix
tfidf = TfidfTransformer()
tfidf.fit(grouped_interactions) # Learn the IDF weights, penalises the common products and promotes the rare ones
new_matrix = tfidf.transform(grouped_interactions) # Apply them

#New matrix is sparse matrix: only cells where value>0 is present else for cell values = 0 those cells are blank
#As we are using item based knn so the rows or index should be Product ids so we done .T at the end to convert rows in col. and vice versa
# Rows = Items, Columns = Users
item_user_matrix = pd.DataFrame(
    new_matrix.toarray(), #the toarray() converts it back appends 0 where cells are blank
    index=grouped_interactions.index, 
    columns=grouped_interactions.columns
).T

print("Item-user matrix created successfully!")
print(f"Products, Users: {item_user_matrix.shape}")

#Saving the user-item matrix dataframe as .csv file
#In this user_item matrix the user_id is the index itself -> pivot (item CF based) 
item_user_matrix.to_csv("data/processed/item_user_matrix.csv")

print(f"File saved as item_user_matrix.csv under {PROJECT_ROOT}/data/processed")