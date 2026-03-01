# Use the ai-recommendation-engine as project root folder as links are all relative to that
# This file generates the .pkl files that the app will use to give recommendations
# Pickle(.pkl) files are python files in which data in in binary format, pickle is an inbuilt library in python. Files go through serialization(converting python objects to binary(aka .pkl files)) and deserialization.

import pickle
import os
import pandas as pd
from sklearn.neighbors import NearestNeighbors

PROJECT_ROOT = os.path.basename(os.getcwd()) #Retrieve the project root folder name
output_data = "data/models"

os.makedirs(output_data, exist_ok=True) #To create models(output) directory if not present

#Defining the file paths in respective variables
interactions = "data/processed/interactions_final.csv"
matrix = "data/processed/item_user_matrix.csv"

# 1. Reading data
print(f"\n1. Reading the pre-processed files...")
df_interactions = pd.read_csv(interactions)
df_matrix = pd.read_csv(matrix, index_col=0)

# 2. Initialise the model
# metric='cosine': Measures the angle (similarity), not distance.
# algorithm='brute': Forces the model to check every item (most accurate).
# n_neighbours says to calculate 20 neighbours for each item
# n_jobs = 1 or -1: -1 mean use the all cpu cores to calculate the similarity(faster), 1 mean use only one core(slower) it only happens during execution(in the app)
print(f"2. Creating the model...")
model = NearestNeighbors(metric="cosine", algorithm="brute", n_neighbors=20, n_jobs=-1)

# 3. Train the model by passing the matrix
# This is lazy learning as it calculates when we ask for it not like as we generated a similarity matrix calculating similarity of each and product with all products. In this the model only calculates for that specific product_id which we clicked.
model.fit(df_matrix)

# 4. Saving the finalised file

# Workflow 
# 1. A user clicks a product
# 2. The app passes that product_id vector taken from matrix to the model
# 3. KNN model calculates and returns the coordinates(index) of the nearest neighbours to the app 
# 4. App passes the coordinates to the matrix and the matrix returns with product_ids
# 5. The App displays that product_ids as recommended products
# So both the .pkl are needed and they work in co-relation, we can use the raw item-user matrix but as .pkl is binary the searching is faster there and app responds faster.
print(f"3. Saving the pickle files...")
with open (os.path.join(output_data, "matrix.pkl"), "wb") as f:
    pickle.dump(df_matrix, f)

with open (os.path.join(output_data,"model.pkl"), "wb") as f:
    pickle.dump(model,f)

with open (os.path.join(output_data, "interactions.pkl"), "wb") as f:
    pickle.dump(df_interactions, f)

print(f"4. .pkl files created and saved at location {PROJECT_ROOT}/{output_data}")