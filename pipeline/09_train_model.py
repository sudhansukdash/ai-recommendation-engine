# Use the ai-recommendation-engine as project root folder as links are all relative to that
# This file generates the .pkl files that the app will use to give recommendations
# Pickle(.pkl) files are python files in which data in in binary format, pickle is an inbuilt library in python. Files go through serialization(converting python objects to binary(aka .pkl files)) and deserialization.

import pickle
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.neighbors import NearestNeighbors

PROJECT_ROOT = os.path.basename(os.getcwd()) #Retrieve the project root folder name
input_data = "data/processed/interactions_clean.csv"
output_data = "data/models"

# 1. Check if the file exists
if not os.path.exists(input_data):
    print(f"File: {input_data} does not exists!")
    exit()

os.makedirs(output_data, exist_ok=True) #To create models(output) directory if not present


# 2. Reading data
print(f"\n1. Reading the file {input_data}...")
interactions = pd.read_csv(input_data)

# 3. Creating user-item matrix
user_item_m = interactions.pivot_table(
    index="user_id",
    columns="pr_id",
    values="scores",
    aggfunc="sum"
).fillna(0)

print(f"2. User-item matrix created successfully!")

# Apply Safety Cap (Clip at 70)
# This prevents obsession (one user clicking 1000 times) from breaking the math
user_item_m = user_item_m.clip(upper=70)

# 4. Applying TF-IDF to de-bias overly populated products to coming in recommendations and keeping unique recommendations

# If we do not de-bias the popular product ex: milk so milk will come in every user recommendation for every product, so if someone buys a laptop he will get recommendations milk as it appears as the neighbour of every item. So to keep recommendations unique we apply tf-idf which also reduces our f1 scores but recommendations are now very unique.
#Tfidf have a significance for which are index and which are columns, for our matrix it looks columns(items) that how many user(index) have interacted with this products so it finds out the product popularity
tfidf = TfidfTransformer()
tfidf.fit(user_item_m) #Learn the overly populated products
user_item_m_tfidf = tfidf.transform(user_item_m) #Apply values learnt punishing the scores of overly common and raising rare items
print(f"3. Applied TfIdf Transformer to the matrix successfully...")

# 5. Transpsoing the matrix 
#As we are performing item-item similarity matrix we are transposing our tf-idf matrix to have index as products and user_id as columns
final_matrix = user_item_m_tfidf.T 
print(f"4. Transposed the matrix successfully!")

# 6. Initialise the model
# metric='cosine': Measures the angle (similarity), not distance.
# algorithm='brute': Forces the model to check every item (most accurate).
# n_neighbours says to calculate 20 neighbours for each item
# n_jobs = 1 or -1: -1 mean use the all cpu cores to calculate the similarity(faster), 1 mean use only one core(slower) it only happens during execution(in the app)
model = NearestNeighbors(metric="cosine", algorithm="brute", n_neighbors=20, n_jobs=-1)

# 7. Train the model by passing the matrix
# This is lazy learning as it calculates when we ask for it not like as we generated a similarity matrix calculating similarity of each and product with all products. In this the model only calculates for that specific product_id which we clicked.
model.fit(final_matrix)
print(f"5. Model created successfully!")

# 8. Saving the finalised file

# Workflow 
# 1. A user clicks a product
# 2. The app passes that product_id vector taken from matrix to the model
# 3. KNN model calculates and returns the coordinates(index) of the nearest neighbours to the app 
# 4. App passes the coordinates to the matrix and the matrix returns with product_ids
# 5. The App displays that product_ids as recommended products
# So both the .pkl are needed and they work in co-relation, we can use the raw item-user matrix but as .pkl is binary the searching is faster there and app responds faster.
with open (os.path.join(output_data, "item_user_matrix.pkl"), "wb") as f:
    pickle.dump(final_matrix, f)

with open (os.path.join(output_data,"knn_model.pkl"), "wb") as f:
    pickle.dump(model,f)

print(f"6. .pkl files created and saved at location {PROJECT_ROOT}/{output_data}")