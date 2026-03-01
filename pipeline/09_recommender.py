#Use the ai-recommendation-engine as project root folder as links are all relative to that
#This script generates recommendations for a particular user_id taking input the matrix and interactions
import pandas as pd
from sklearn.neighbors import NearestNeighbors

# 1. Load the data
matrix = pd.read_csv("data/processed/item_user_matrix.csv", index_col=0) #Rows = products, cols = users
interactions = pd.read_csv("data/processed/interactions_final.csv")

#2. Train the model with matrix
model = NearestNeighbors(metric="cosine", algorithm="brute", n_jobs=-1, n_neighbors=10)
model.fit(matrix) #Feed the matrix to the model

#3. Define a fixed user_id
user = "U101"

#4. Cold start logic, when user is not in dataset
if user not in matrix.columns:
    print(f"User {user} not found in database. Triggering Cold Start logic...")

    # Recommend the top 'n' most interacted products
    popular_items = interactions["pr_id"].value_counts().head().index.tolist()
    print(f"Top 5 Recommendations: {popular_items}")

else:
    #Filter interacted products, interactions["user_id"] == user creates a boolean mask, in every user_id col the id that matches user are true else others are false, then we pass it as interactions[...], it filters out and keeps only the true values(actual user_id not booleans)
    user_data = interactions[interactions["user_id"] == user]
    
    #Logic of retargetting: if scores > 30 user already bought it, do not recommend again, else scores <= 30 recommend
    bought = user_data[user_data["total_scores"] > 30]

    #Set of only product ids where scores > 30
    bought_id = set(bought["pr_id"])

    #5. User history
    user_vector = matrix[user] #Vector having transformed scores with every product_id
    interacted = user_vector[user_vector > 0].index.tolist() #Keep only the products the user have history with >0

    #Empty list that will contain the recommendations
    candidates = []

    print(f"User {user} interacted with {len(interacted)} products! Generating recommendations...")
    for item in interacted:
        item_vector = matrix.loc[[item]] # [[item]] because we want a 2D array 1*n because model kneighbours accepts a 2d array

        #Calculate the closest to the product vector, give distances(how close) and indices(row no.)
        distances, indices = model.kneighbors(item_vector, n_neighbors=10)
        
        #Kneigbours will return a nested list (lists of lists)
        distances = distances.flatten()
        indices = indices.flatten()

        #This loop is used to get the names of the ids from the indices and their respective distances
        for i in range(len(indices)):
            neigbour_name = matrix.index[indices[i]]
            distance = distances[i]
            
            #Do not recommend the same item and also do not recommend the bought items
            if neigbour_name != item and neigbour_name not in bought_id:
                candidates.append((neigbour_name, distance))

    final_recommendations = []
    #Selecting recommendations from a pool of candidates
    #Sorting logic acc. to closest distance, i.e the closest distance the most similar the  product
    unique_list = bought_id.copy() #Contains already purchased items + items that are already being recommended, suppose P12 exists 2 times in candidates and once it already been recommended so it might get recommended again(two times) if we explicitly do not say that dont recommend this product
    
    #Sort candidates according to increasing distance
    candidates.sort(key=lambda x:x[1])
    for prod, dist in candidates:
        #Check if user already bought it or is in recommendations
        if prod not in unique_list:
            final_recommendations.append(prod)
            unique_list.add(prod)

            #Give 6 recommendations
            if len(final_recommendations) ==6:
                break
    
    print(f"Top 5 Recommendations: {final_recommendations}")
