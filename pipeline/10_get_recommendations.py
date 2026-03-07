# Use the ai-recommendation-engine as project root folder as links are all relative to that
# This file gives recommendations for a user id using the get_recommendations function from utils in terminal
import os
import sys
import pickle
import time
import random

# This allows the script to find your 'utils' folder and also make sure we can run this file directly using run button instead of following the pythom -m... approach
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Import the function from utils
from utils.recommender import get_user_recommendations

# Load the files
print("Loading Models and Data...")
# 'rb' is read binary mode and as we are reading pickle files, we use pickle.load(filename)
with open("data/models/matrix.pkl", "rb") as f: 
    matrix = pickle.load(f)
with open("data/models/model.pkl", "rb") as f: 
    model = pickle.load(f)
with open("data/models/interactions.pkl", "rb") as f: 
    interactions = pickle.load(f)

# User id for which we want recommendations, we can also specify the user id like "U20381" and check for cold start logic
TARGET_USER_ID = interactions['user_id'].iloc[0] 
# Grabs a random product from matrix to test 
LIVE_PRODUCT_ID = random.choice(matrix.index.tolist())

print("\n" + "=" * 60)
print(f" TESTING RECOMMENDATION ENGINE FOR USER: {TARGET_USER_ID}")
print("=" * 60 + "\n")

# 4. TEST 1: Baseline recommendations from dataset
print("--- TEST 1: STRICTLY HISTORICAL (No Live Clicks) ---")

# use the function and pass the arguments, here skipped the optional arguments session_history and blacklist 
recs_historical = get_user_recommendations(
    user_id=TARGET_USER_ID,
    matrix=matrix,
    interactions=interactions,
    model=model,
)

print("Top 5 Recommendations based on past history:")
# This prints in a list wise format (1. 2...) instead of printing the raw recs_historical[:5]
i = 1
for rec in recs_historical[:5]:
    print(f"  {i}. Product: {rec['id']} (Distance: {rec['distance']})")
    i += 1


# 5. TEST 2: SIMULATING A LIVE CLICK
print("\n--- TEST 2: SIMULATING A LIVE INTERACTION ---")
print(f"⚡ User just clicked 'PURCHASE' on Product ID: -> {LIVE_PRODUCT_ID} <- ⚡")

# Creating the fake session history payload (Weight 30 = Purchase)
fake_live_click = [
    {'pr_id': LIVE_PRODUCT_ID, 'weight': 30, 'time': time.time()} 
]

recs_live = get_user_recommendations(
    user_id=TARGET_USER_ID,
    matrix=matrix,
    interactions=interactions,
    model=model,
    session_history=fake_live_click, # Passing the live click!
)

# Printing recommendations again after the purchase to compare if the recommendations changed or not
print(f"\nTop 5 Recommendations AFTER live interaction with {LIVE_PRODUCT_ID}:")
j = 1
for rec in recs_live[:5]:
    print(f"  {j}. Product: {rec['id']} (Distance: {rec['distance']})")
    j += 1
print(f"\n{'=' * 55}\n")