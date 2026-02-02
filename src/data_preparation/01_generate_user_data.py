#Use the ai-recommendation-engine as project root folder as links are all relative to that
#Generate users user_data using random module and introducting inconsistencies
import random, pandas as pd
from faker import Faker #used faker to generate names, emails
import os

#The seed(42) ensures libraries generate same data no matter how many times we run this script
random.seed(42)
Faker.seed(42)
#Return the project root folder name
PROJECT_ROOT = os.path.basename(os.getcwd())

# Initialize Faker for Indian names
fake = Faker('en_IN')
users = []

print("\nStarting user data generation...")

#Introduced casing, spacing inconsistencies, typos in field "city" to demonstrate real-world user_data
#There are 14 unique citites
city = [
  
    "Rourkela", "rourkela", "ROURKELA", "rourkela ",
    "Bhubaneswar", "bhubaneswar", "BHUBANESWAR", "Bhubneswar", # Typo
    "Mumbai", "mumbai", "MUMBAI", "mumbai ",
    "New Delhi", "new delhi", "NEW DELHI", "new_delhi", "New Delhi ",
    "Kolkata", "kolkata", "KOLKATA", "kolkata ",
    "Pune", "pune", "PUNE", "Pune ",
    "Bangalore", "bangalore", "BANGALORE", "bangalore ",
    "Chennai", "chennai", "CHENNAI", "chennai ",
    "Hyderabad", "hyderabad", "HYDERABAD", "Hyderbad", # Typo
    "Ahmedabad", "ahmedabad", "AHMEDABAD", "ahmedabad ",
    "Jaipur", "jaipur", "JAIPUR", "jaipur ",
    "Lucknow", "lucknow", "LUCKNOW", "Lucknow ",
    "Chandigarh", "chandigarh", "CHANDIGARH", "Chandigarh ",
    "Indore", "indore", "INDORE", "indore ",
    None
]

#Introduced casing, spacing inconsistencies in field "employment_status" to demonstrate real-world user_data
# 3 Unique status: student, employed, not employed
employment_status = ["Student ","Employed","Not employed","STUDENT","employed ","NOTemployed","not_employed","student","employed",None]

#Creating 1200 users with 3 fields user_id, city, employement status
for i in range(1200):
    
    fname = fake.first_name()
    lname = fake.last_name()
    email = f"{fname.lower()}.{lname.lower()}{10+i}@example.com"
    
    #Making a dictionary 
    user_data = {
        "user_id":f"U{random.randint(1,900)}",
        "first_name" : fname,
        "last_name" : lname,
        "email" : email,
        "password" : "password123",
        "city":random.choice(city),
        "employment_status":random.choice(employment_status)}

    #Appending the dictionary to the list, each dictionary is an item in list
    users.append(user_data)

#Using DataFrame from pandas to convert list of dictionaries into tables(rows and columns)
df = pd.DataFrame(users)

print(df.info())

print("\nUser data generation successful!")
#Convert dataframe to csv file using to_csv function
df.to_csv("data/raw/users_raw.csv", index=False)

print(f"File saved as users_raw.csv under {PROJECT_ROOT}/data/raw/")