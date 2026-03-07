# This is the master-file of the recommendation logic from here we import functions throughout our files to get recommendations

# This function generates the "Recommended for you" section in our app
def get_user_recommendations(user_id, matrix, interactions, model, session_history=None, blacklist=None):
    
    #Initialise empty structures as session_history and blacklist are optional arguments in function, preventing error if they are not passed
    if session_history is None: session_history = []
    if blacklist is None: blacklist = set()

    scored_history = {}

    # 1. Load Static History, taking the historical interactions in datasets, reducing their weight to 0.1 so that the live interactions are carry more weight, added time=0 for interactions in datasets, i.e, they are infinitely old
    static_history = interactions[interactions['user_id'] == user_id]['pr_id'].unique().tolist()
    for pid in static_history:
        scored_history[pid] = {'weight': 0.1, 'time': 0} 

    # 2. The live weighing logic used a multiplier of 50, so that our live interactions have a greater weigh and overpower the generated history data (only for live demo)
    for interaction in session_history:
        pid = interaction['pr_id']
        w = interaction['weight'] * 50 #Multiplier of 50
        t = interaction['time']
        
        # If the item is not in history, add it
        if pid not in scored_history:
            scored_history[pid] = {'weight': w, 'time': t}
        else:
            # If the item is already in history and same action just update the timestamp to recent else if other action taken(bought) then update the weight along with time (Keep only the maximum intent)
            if w > scored_history[pid]['weight']:
                scored_history[pid]['weight'] = w
            if t > scored_history[pid]['time']:
                scored_history[pid]['time'] = t

    # 3. THE "RECENCY-FIRST":
    # We sort by TIME (t) first, then WEIGHT (w).
    # This ensures the Necklace from 1 minute ago beats the Phone from 10 minutes ago.
    sorted_history_items = sorted(
        scored_history.keys(), 
        key=lambda k: (scored_history[k]['time'], scored_history[k]['weight']), 
        reverse=True
    )
    
    # Grab the top 5 most recent "Seed" items to find neighbors for
    seeds = sorted_history_items[:5]
    
    # Cold Start fallback: if the user has just signed up (no history) show him the top 20 most interacted products in the dataset
    if not seeds:
        fallback_ids = interactions['pr_id'].value_counts().head(20).index.tolist()
        return [{"id": pid, "distance": None} for pid in fallback_ids]

    # 4. Find K-Nearest Neighbors for the Seed items
    candidates = []
    seen_candidates = set()

    for seed_id in seeds:
        if seed_id in matrix.index:
            seed_weight = scored_history[seed_id]['weight']
            
            query_vector = matrix.loc[[seed_id]]
            #Fetch the top 10 vectors for the seed
            dists, indices = model.kneighbors(query_vector, n_neighbors=10)
            
            #Flatten the 2d to 1d
            dists = dists.flatten()
            indices = indices.flatten()
            
            for i in range(len(indices)):

                #As distances and indices are mathematically values only for now use them to find the score and the actual product id
                neighbor_name = matrix.index[indices[i]]
                raw_dist = dists[i]
                
                # Effective distance ensures the weight still matters for the final ranking
                effective_dist = raw_dist / seed_weight
                
                # Ignore the products if they are blacklisted(removed from cart), user already bought (higher weight) and they already not exist in list
                if (neighbor_name not in blacklist and 
                    neighbor_name not in scored_history and 
                    neighbor_name not in seen_candidates):
                    
                    #Append to candidates list
                    candidates.append((effective_dist, raw_dist, neighbor_name))
                    seen_candidates.add(neighbor_name)

    # Sort the tuples according to the effective distance
    candidates.sort()
    
    #Fetch the top 20 candidates which we will show in recommendations
    top_20_results = []
    for c in candidates[:20]:
        top_20_results.append({
            "id": c[2],  #c[2] where c is the tuple and 2 is the index which refers to the products id
            "distance": round(c[1], 4) #c[1] is the raw distance rounded to 4 points
        })
        
    return top_20_results

# This function gives the recommendations within the product details page, i.e., similar to the product
def get_similar_products(product_id, matrix, model, blacklist=None):
    # Empty set for optional argument
    if blacklist is None: blacklist = set()
    # If we have added a new product and the matrix is still trained in the old list
    if product_id not in matrix.index:
        return []

    query_vector = matrix.loc[[product_id]]
    #Find 11 similar vectors which will include the product viewed itself
    dists, indices = model.kneighbors(query_vector, n_neighbors=11) 
    
    related_results = []
    dists = dists.flatten()
    indices = indices.flatten()

    # Ignore the blacklisted and the product itself and append the name(id) and raw_distance as a tuple in the related results list and return the list
    for i in range(len(indices)):
        neighbor_name = matrix.index[indices[i]]
        raw_dist = round(dists[i], 4)
        
        if neighbor_name != product_id and neighbor_name not in blacklist:
            related_results.append({"id": neighbor_name, "distance": raw_dist})
            
    return related_results