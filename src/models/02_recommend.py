#Use the ai-recommendation-engine as project root folder as links are all relative to that
#This file gives a list of top recommendations for a user using the user matrix and item similarity matrix

import pandas as pd
import random

#Read the user_item_matrix and item_similarity matrix csv files
user_item_m = pd.read_csv("../ai-recommendation-engine/data/processed/user_item_matrix.csv", index_col=0)
item_similarity_m = pd.read_csv("../ai-recommendation-engine/data/processed/item_similarity_matrix.csv", index_col=0)

# print(user_item_m.head())
#user-id for which we want recommendations
user_id = "U101"

#Retrieve the row with interaction values with different product
user_row = user_item_m.loc[user_id]
# print(user_row)

#Keep only those entries where the user interacted with products, views-> weight = 1 are considered
user_filtered = user_row[user_row>=1]  #From user_row, keep only those entries where the condition user_row >=1 is True.
# print(user_filtered.index)

user_interacted = user_filtered.index #Returns index of series containing the pr-id's the user interacted with earlier
# print(user_interacted)

#Making a dictionary to store pr_id's as keys and aggregate similarity scores for products to recommend
scores = {}

for product_id in user_interacted: #for each product_id in user_interacted do this...
   
    #Returns a row for similarity scores of that product id with other products in similarity matrix
    product_vector = item_similarity_m.loc[product_id]
    
    #Delete that product from that series, we are not recommending the same product user already interacted with
    product_vector = product_vector.drop(product_id)

    weight = user_filtered[product_id]
    #In that series retrieve (candidate_id,similarity score) for each product
    #.items() is a series method that returns index as well as values in form (index,value)
    for candidate_id, similarity_score in product_vector.items():

        #If a product is already what user interacted with earlier skip the loop and jump to next pr_id
        if candidate_id in user_interacted:
            continue
        
        #scores.get(candidate_id, 0) will return value for key candidate_id, if the candidate id does not exist it will return 0
        #Add the similarity score and update the value of the key in scores dictionary
        scores[candidate_id] = scores.get(candidate_id, 0) + similarity_score*weight

#To sort these scores according to values we use sorted() which is an inbuilt python function, that takes a list like collection as an input and returns a new list where those specific items are sorted in order
#lambda x is a tiny function without a name, we use here lambda x:x[1], which mean take one item x from list and use x[1] for sorting

#3 arguments list to sort, condition on which basis to sort, order if no reverse = True sorts in ascending order
sorted_score = sorted(scores.items(), key = lambda x:x[1], reverse=True) 

#Take no of recommendations to show from user
n = int(input(f"How many item recommendations you want for {user_id}: "))
top_n = sorted_score[:n] #Only take elements till 'n' index in top_n
# print(top_n)

#Only product id of top_n not similarity scores
recommended_products = []

#Logic to display only pr_id 
for tup in top_n:
    p_id = tup[0]
    recommended_products.append(p_id)

print(f"The top {n} recommendations are: {recommended_products} ")