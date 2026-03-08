# Use the ai-recommendation-engine as project root folder as all links are relative to that
# This script gives precision, recall and f1 scores based on which we can evaluate our recommendations
import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize

# 1. Setup the project root so we can import easily from utils the recommendation f(n)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)
# Importing get_user_recommendaations to evaluate from utils/recommender
from utils.recommender import get_user_recommendations

print("1. Loading Clean CSV Data")
# Loading the interactions_final.csv for the data
csv_path = os.path.join(PROJECT_ROOT, "data", "processed", "interactions_final.csv") 
interactions = pd.read_csv(csv_path)

print("2. Splitting the data into train-test...")

# Count the rows(interactions) for each user
user_counts = interactions.groupby('user_id')['user_id'].transform('count')

# Split directly using that count for train and test, keep the users that have < 5 interactions as train only >=5 some are kept as train and some are test
eligible_data = interactions[user_counts >= 5]
train_non_eligible = interactions[user_counts < 5]

# Use sklearn to split the eligible users data into train data and test data
train_eligible, test_interactions = train_test_split(
    eligible_data, 
    test_size=0.2, # Hide 20% (test data)
    stratify=eligible_data['user_id'], # By default sklearn considers the entire file and hides 20% of it, this line ensures for each eligible user we are hiding 20% instead of overall which ensures consistency 
    random_state=42 # To ensure we get the same scores always
)

# Recombine the training data one part was users who were not eligible and one which we got by splitting
train_interactions = pd.concat([train_eligible, train_non_eligible])

print(f"\nTotal Interactions: {len(interactions)}")
print(f"Training Interactions: {len(train_interactions)}")
print(f"Testing Interactions: {len(test_interactions)}\n")

print("3. Building Zero-Leakage Matrix & Model")
# Build matrix safely from training data which will be passed to the model
raw_train_matrix = train_interactions.pivot_table( index='user_id', columns='pr_id', values='total_scores').fillna(0)

# Normalize the matrix using l2 and transpose(Item-user)
matrix_values = normalize(raw_train_matrix.values, norm='l2', axis=0)
train_matrix = pd.DataFrame(
    matrix_values, index=raw_train_matrix.index, columns=raw_train_matrix.columns
).T

# Train Model
model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20)
model.fit(train_matrix)
print("4. Matrix and model built successfully.\n")

print("5. Evaluating recommendation engine performance...")
precisions, recalls = [], []

# 1. THE SPEED FIX: Group the data into dictionaries before looping this gives us instant lookups instead of scanning the DataFrame thousands of times
hidden_items_dict = test_interactions.groupby('user_id')['pr_id'].apply(set).to_dict()
train_history_dict = dict(tuple(train_interactions.groupby('user_id')))

total_test_users = len(hidden_items_dict)

# Iterate directly through our clean dictionary
for idx, (user, hidden_set) in enumerate(hidden_items_dict.items(), 1):
    if idx % 50 == 0:
        print(f"  Processed {idx}/{total_test_users} test users...")
        
    # Instantly grab the user's history (or an empty DataFrame if they have none)
    user_train_history = train_history_dict.get(user, pd.DataFrame())
    
    # Generate predictions
    recs = get_user_recommendations(user, train_matrix, user_train_history, model)
    
    # THE CLEANUP: Use a Set Comprehension directly (faster than making a list then converting to a set)
    rec_set = {rec["id"] for rec in recs}
    
    # Calculate True Hits using simple set intersection
    hits = len(rec_set & hidden_set)
    
    precisions.append(hits / len(rec_set) if rec_set else 0.0)
    recalls.append(hits / len(hidden_set) if hidden_set else 0.0)

# 5. FINAL SCORES
avg_precision, avg_recall = np.mean(precisions), np.mean(recalls)
f1_score = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall) if (avg_precision + avg_recall) > 0 else 0.0

print(f"{'=' * 45}")
print("    ZERO-LEAKAGE EVALUATION METRICS")
print(f"{'=' * 45}")
print(f"Precision@20 : {avg_precision:.4f}")
print(f"Recall@20    : {avg_recall:.4f}")
print(f"F1-Score     : {f1_score:.4f}")
print(f"{'=' * 45}")