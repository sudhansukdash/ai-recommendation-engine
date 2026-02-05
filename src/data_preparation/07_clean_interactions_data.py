#Use the ai-recommendation-engine as project root folder as links are all relative to that
#Cleaning interactions_raw.csv using pandas

import pandas as pd
import os

#Return the project root folder name
PROJECT_ROOT = os.path.basename(os.getcwd())

print("\nStarting interaction data cleaning...")

#Reading the interactions_raw.csv and storing it in a DataFrame
raw_interactions = pd.read_csv("data/raw/interactions_raw.csv")
clean_interactions = raw_interactions.copy()

#Dropping NaN values
clean_interactions = clean_interactions.dropna(subset=["user_id", "pr_id", "interaction_type"])

#Handling inconsistencies in interaction_type
# print(clean_interactions.value_counts("interaction_type", dropna=False))
clean_interactions["interaction_type"] = clean_interactions["interaction_type"].str.lower().str.strip()
# print(clean_interactions.value_counts("interaction_type", dropna=False))

#It groups the duplicate ['user_id', 'pr_id', 'interaction_type'] in a single row and counts occurances of such rows (.size()) and creates a new column named frequency where the count is stored. Here only completely same rows are grouped for ex U1,P1, view has been grouped but u1,p1,purchase might exist which we will handle in user_item_matrix
#It retains if user have bought and item 2 times insteading of deleting such interactions which would have a stronger recommendation.
#Now the clean_interactions have fields user_id, product_id, interaction_type, frequency
clean_interactions = clean_interactions.groupby(['user_id', 'pr_id', 'interaction_type']).size().reset_index(name='frequency')
# print(clean_interactions.value_counts(subset="interaction_type"))

#After cleaning interactions we are using a weight map to replace the strings in interaction_type to actual values that model understand
weight_map = {
    "view" : 0.5,
    "wishlist": 3,
    "cart": 5,
    "purchase" : 30

}

#Create a new col. weight and use the weight_map and interaction_type col from df to add values accordingly here
clean_interactions['weight'] = clean_interactions["interaction_type"].map(weight_map)
#If any values left to add in weight_map it fills NaN with 0
clean_interactions["weight"] = clean_interactions["weight"].fillna(0)
# print(clean_interactions)

#Now giving scores to each row using frequency and weight
clean_interactions["scores"] = clean_interactions["weight"] * clean_interactions["frequency"]
# Remove meaningless interactions (score 0)
clean_interactions = clean_interactions[clean_interactions['scores'] > 0]
#Dropping the col. interaction_type,weight as it no more needed 
clean_interactions = clean_interactions.drop(columns=["interaction_type","weight"])
# print(clean_interactions.head())

print(clean_interactions.info())
print("\nInteraction data cleaned successfully!")

#Saving this clean_interactions dataframe into a new interactions_clean.csv file
clean_interactions.to_csv("data/processed/interactions_clean.csv", index=False)

print(f"File saved as interactions_clean.csv under {PROJECT_ROOT}/data/processed/")