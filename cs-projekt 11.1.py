#!/usr/bin/env python
# coding: utf-8

# In[1]:


pip install requests


# In[ ]:


import requests
import pandas as pd
from IPython.display import display, Image


# # API functions

# In[6]:


# Function to extract 'title' from categories
def extract_titles(categories):
    return [category['title'] for category in categories]


# In[7]:


#Function to only exctract the first addresse line
def extract_addresse(location):
    return location.get('address1', '')


# In[8]:


#Hauptfunktion 1 um informationen vom API zu holen 
def get_restaurants_location_clean(location):
    #calling the API    
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {
        "Authorization": "Bearer EN2FsqhUn487c-Hh4FeZGlJKk9i6bCC1kW45fmc4TQx1zw2sQ8CNGM57G3olkT4OYLcDtHHU_PVyJKaIIboLtnlVledeI6-UAwAor6xhNLIZxxqQ-EgExHGMXDAlZnYx"
    }
    params = {
        "term": "restaurants",
        "location": f"{location}"
    }
    response = requests.get(url, headers=headers, params=params)
    json_testing = response.json()
    
    #transforming the Json content from the API into a data frame 
    df_testing = pd.DataFrame(json_testing["businesses"])
    
    #only getting the columns for name, categories and location
    nice_format = df_testing[["name", "categories", "location"]]
    
    # Applying the function to the 'categories' column
    nice_format['category_titles'] = nice_format['categories'].apply(extract_titles)
    
    # Applying the function to the 'categories' column
    nice_format['location'] = nice_format['location'].apply(extract_addresse)
    
    #removing the brackets from the category titles, by first turing the column into strings and then using the strip 
    # function to remove it. 
    nice_format["category_titles"] = nice_format["category_titles"].astype(str)
    nice_format["category_titles"] = nice_format["category_titles"].str.strip('[')
    nice_format["category_titles"] = nice_format["category_titles"].str.strip(']')
    nice_format["category_titles"] = nice_format["category_titles"].str.strip("''")
    
    #dropping the categories column, since we extracted the necessariy information and put it into the category_titles column, that we made
    nice_format_1 = nice_format.drop('categories', axis=1)
    
    
    return nice_format_1


# In[9]:


#Hauptfunktion 2 um informationen vom API zu holen 
def get_restaurants_location(location):
    #calling the API     
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {
        "Authorization": "Bearer EN2FsqhUn487c-Hh4FeZGlJKk9i6bCC1kW45fmc4TQx1zw2sQ8CNGM57G3olkT4OYLcDtHHU_PVyJKaIIboLtnlVledeI6-UAwAor6xhNLIZxxqQ-EgExHGMXDAlZnYx"
    }
    params = {
        "term": "restaurants",
        "location": f"{location}"
    }
    response = requests.get(url, headers=headers, params=params)
    json_testing = response.json()
    
    #transforming the Json content from the API into a data frame 
    df_testing = pd.DataFrame(json_testing["businesses"])
    
    #making a new datafrme with these columns, so we have a dataframe with all the information we need
    business_df = df_testing[["id", "name", "image_url", "categories", "location"]]  
    
    return business_df


# In[10]:


#funktion 1 callen
locations = get_restaurants_location("St.Gallen")


# In[11]:


#gettting locations dataframe 
locations


# In[12]:


#function 2 callen
locations_clean = get_restaurants_location_clean("St.Gallen")


# In[15]:


#getting locations clean data frame 
locations_clean


# # getting images 

# In[13]:


#Built a function to display the pictures eith by their id or name 
def get_picture_of_restaurant(df, restaurant_id=None, restaurant_name=None):
    if restaurant_id:
        matching_rows = df[df['id'] == restaurant_id]
    elif restaurant_name:
        matching_rows = df[df['name'].str.contains(restaurant_name, case=False, na=False)]
    else:
        return "No restaurant specified!"

    #if there are no matches, both id or name it will return this
    if matching_rows.empty:
        print("No matching restaurant found.")
    else:
        for _, row in matching_rows.iterrows():
            display(Image(url=row['image_url']))


# In[14]:


#returning pictures of restsuarants based on id
byid = get_picture_of_restaurant(locations, restaurant_id='OBeg8ZM_n8deI6Rvur_oDw')


# In[16]:


#returning pictures of restsuarants based on name
name = get_picture_of_restaurant(locations, restaurant_name='focacceria')


# # Database

# In[ ]:


# Define the DataFrame with specific types to avoid type issues
database = pd.DataFrame({
    'id': pd.Series(dtype='int'),
    'restaurant': pd.Series(dtype='str'),
    'comment': pd.Series(dtype='str'),
    'name': pd.Series(dtype='str'),
    'rating': pd.Series(dtype='str'),
    'ID': pd.Series(dtype='str')
})


# In[ ]:


def add_entry_to_df():
    global database  # Reference the global DataFrame

    # Generate the next ID
    next_id = database['id'].max() + 1 if not database.empty else 1
    
    # Collect user inputs
    restaurant = input("Enter the restaurant name: ")
    comment = input("Enter your comment: ")
    name = input("Enter your name: ")
    rating = input("How do you rate this restaurant from 5: ")
    ID = input("Enter restaurant ID: ")

    # Create a dictionary with the new data
    new_data = {
        'id': next_id,
        'restaurant': restaurant,
        'comment': comment,
        'name': name, 
        'rating': rating,
        'ID': ID
    }

    # Append new data to the global DataFrame
    new_data_df = pd.DataFrame([new_data])
    database = pd.concat([database, new_data_df], ignore_index=True)


# In[ ]:


#adding stuff to the made dataframe with the function
add_entry_to_df()


# In[20]:


#calling the database
database


# In[ ]:


def only_restaurant(name_restaurant):
    return database.loc[database[restaurant] == f"{name_restaurant}]


# In[ ]:


def specific_person(person_name):
    

