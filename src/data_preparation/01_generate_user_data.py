#Use the ai-recommendation-engine as project root folder as links are all relative to that
#Generate users user_data using random module and introducting inconsistencies
import random, pandas as pd
users = []

print("Starting user data generation...\n")
#Introduced casing, spacing inconsistencies in field "city" to demonstrate real-world user_data
#There are 7 unique citites: rourkela, bhubaneswar, mumbai, pune, new delhi, kolkata, bangalore
city = ["Rourkela","Bhubaneswar","Mumbai","New Delhi","kolkata","Pune","Bangalore","rourkela","BHUBANESWAR","KOLKATA","NEW DELHI ","mumbai","kolkata ","bangalore ","new_delhi","pune","bhubaneswar","bangalore",None]

#Introduced casing, spacing inconsistencies in field "employment_status" to demonstrate real-world user_data
# 3 Unique status: student, employed, not employed
employment_status = ["Student ","Employed","Not employed","STUDENT","employed ","NOTemployed","not_employed","student","employed",None]

#Creating 1200 users with 3 fields user_id, city, employement status
for i in range(1200):
    
    #Making a dictionary 
    user_data = {
        "user_id":f"U{random.randint(1,900)}",
        "city":random.choice(city),
        "employment_status":random.choice(employment_status)}

    #Appending the dictionary to the list, each dictionary is an item in list
    users.append(user_data)

#Using DataFrame from pandas to convert list of dictionaries into tables(rows and columns)
df = pd.DataFrame(users)

print(df.info())

print("\nUser data generation successful!")
#Convert dataframe to csv file using to_csv function
df.to_csv("../ai-recommendation-engine/data/raw/users_raw.csv", index=False)

print("File saved as users_raw.csv under ai-recommendation-engine/data/raw/")