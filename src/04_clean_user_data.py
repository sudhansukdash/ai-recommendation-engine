#Use the ai-recommendation-engine as project root folder as links are all relative to that
#Cleaning users_raw.csv using pandas

import pandas as pd
print("Starting user data cleaning...")

#Reading the raw file into a DataFrame
raw_users = pd.read_csv("../ai-recommendation-engine/data/raw/users_raw.csv")
clean_users = raw_users.copy()
# print(raw_users) #Before cleaning
# print(raw_users.info())

#Cleaning the file column by column

#Cleaning column: user_id
# print(clean_users.value_counts(subset="user_id",dropna=False))
clean_users = clean_users.drop_duplicates(subset=["user_id"])
clean_users = clean_users.dropna(subset="user_id")
# print(clean_users.value_counts(subset="user_id",dropna=False))

#Cleaning column: city
# print(clean_users.value_counts(subset="city",dropna=False))
clean_users["city"] = clean_users["city"].str.lower().str.strip().str.replace(" ", "_")
clean_users["city"] = clean_users["city"].fillna("missing")
# print(clean_users.value_counts(subset="city",dropna=False))

#Cleaning column: employment_status
# print(clean_users.value_counts(subset="employment_status",dropna=False))
clean_users["employment_status"] = clean_users["employment_status"].str.lower().str.strip().str.replace(" ","_").replace("notemployed","not_employed")
clean_users["employment_status"] = clean_users["employment_status"].fillna("missing")
# print(clean_users.value_counts(subset="employment_status",dropna=False))


print("User data cleaned successfully!\n")
print(clean_users.info())

#Saving this clean_users dataframe into a new users_clean.csv file
clean_users.to_csv("../ai-recommendation-engine/data/processed/users_clean.csv", index=False)

print("File saved as users_clean.csv under ai-recommendation-engine/data/processed/")