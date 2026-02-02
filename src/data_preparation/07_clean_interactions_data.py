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

#Interactions must be cleaned row-wise not indivisual column-wise
clean_interactions = clean_interactions.drop_duplicates() #Cleaning only same user_id, pr_id, interaction_type pair rows

print(clean_interactions.info())
print("\nInteraction data cleaned successfully!")

#Saving this clean_interactions dataframe into a new interactions_clean.csv file
clean_interactions.to_csv("data/processed/interactions_clean.csv", index=False)

print(f"File saved as interactions_clean.csv under {PROJECT_ROOT}/data/processed/")