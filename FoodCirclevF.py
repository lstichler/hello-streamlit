#DISCLAIMER: Die beiden Studentinnen, die den Code erstellt haben (Elena Maehrle und Alina Bricker), verfügten bereits vor dem Kurs gute Programmierkenntnisse 
#Daher brauchten sie nicht so viel externe Hilfe von Websites oder Chatgtp, aber wo solche Externe Hilfe beansprucht wurde, wurde es klar gekennzeichnet

# Importieren der benötigten Libaries
import streamlit as st
import pandas as pd
import requests

# Definition des Hintergrundbildes 
# Source: https://discuss.streamlit.io/t/how-do-i-use-a-background-image-on-streamlit/5067/5
def set_bg_image():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://cdn.pixabay.com/photo/2016/10/20/20/47/background-1756615_1280.jpg");
            background-size: cover;
            background-position: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Aufrufen der zuvor definierten Funktion
set_bg_image()

# Anzeigen des Logos
# Source: https://docs.streamlit.io/develop/api-reference/media/st.image
st.image("Logo Food Cirlce.png", width=150)

# Aufrufen der Yelp-API, um Restaurants basierend auf eine gegebene Location 
# Source: https://docs.streamlit.io/develop/api-reference, ource: How to use API, help from chatgtp, prompt: "I want to work with this API: https://api.yelp.com/v3/businesses/search
#                                                              I have an api key and authorization, but I haven't been able yet to figure out how to actually call 
#                                                               on the function and then receive output. could you provide me with the first coding steps for how to call the api "

def get_restaurants(location):
    # URL der API
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {
        "Authorization": "Bearer 6fvAUhr3oMOOOEmGybAjxAoqlAmWx31FhbvGnWw5R8jIhAfvIZVSXmT4GFYMeJsGKwb-0zX_pfD_CMpIVtEzHBdZ10EZ-fvzHkb_PYhtiJ9BHx4Ng359IGfz8Ak-ZnYx",
        # Verwendung eines User Agent, da es nur mit dem Authorization Key nicht funktioniert hat, sprich die API hat keinen Output returned. 
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
        "accept": "application/json"
    }
    params = {
        "term": "restaurants",
        "location": location
    }
    response = requests.get(url, headers=headers, params=params)
    # Umwandlung in json
    data = response.json()
    if data and "businesses" in data:
        # Umwandung von nur businesses in ein pandas data frame
        df = pd.DataFrame(data["businesses"])
        # Längen- und Breitengrad extrahieren, wenn Koordinaten vorhanden sind
        df['lat'] = df['coordinates'].apply(lambda x: x.get('latitude') if isinstance(x, dict) else None)
        df['lon'] = df['coordinates'].apply(lambda x: x.get('longitude') if isinstance(x, dict) else None)
        return df
    else:
        return pd.DataFrame()

# Zeigen des Titels der Anwendung
# Source: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state, https://docs.streamlit.io/develop/api-reference/data/st.dataframe, ChatGPT by OpenAI zur Behebung von Fehlern im Code
def main():
    st.title("FoodCircle")
    
    # Diese Zeile überprüft, ob in der aktuellen Session eine Tabelle für Bewertungen existiert. Wenn nicht, wird eine leere Tabelle mit den Spalten Restaurant, Comment, Name, Rating und Restaurant ID erstellt.
    if 'reviews' not in st.session_state:
        st.session_state.reviews = pd.DataFrame(columns=['Restaurant', 'Comment', 'Name', 'Rating', 'Restaurant ID'])

    # Der Benutzer gibt einen Ort ein
    location = st.text_input("Enter a location (e.g., 'San Francisco')", "")
    if location:
        restaurants_df = get_restaurants(location)
        if not restaurants_df.empty:
            # Wenn Restaurants gefunden wurden, kann der Benutzer ein Restaurant auswählen 
            restaurant_choice = st.selectbox("Select a restaurant", restaurants_df['name'])
            restaurant_id = restaurants_df[restaurants_df['name'] == restaurant_choice]['id'].iloc[0]
            
            # Der Benutzer gibt seinen Namen, seinen Kommentar und seine Bewertung ein
            name = st.text_input("Your name")
            comment = st.text_area("Your comment")
            rating = st.slider("Your rating", 1, 5, 1)
            
            # Der Nutzer drückt den Submit Button
            # Source: https://pandas.pydata.org/docs/reference/api/pandas.concat.html
            submit_pressed = st.button("Submit Review")
            if submit_pressed:
                new_review = pd.DataFrame([{
                    'Restaurant': restaurant_choice,
                    'Comment': comment,
                    'Name': name,
                    'Rating': rating,
                    'Restaurant ID': restaurant_id
                }])
                st.session_state.reviews = pd.concat([st.session_state.reviews, new_review], axis=0)
                st.success("Review submitted successfully!")

                # Die zuletzt eingereichte Bewertung wird angezeigt
                st.subheader("Recently Submitted Review:")
                st.table(st.session_state.reviews.tail(1)) 

            # Bewertungen werden angezeigt
            if not st.session_state.reviews.empty:
                st.subheader("All Reviews:")
                
                # Benutzer kann nach Namen und Bewertungen filtern
                # Source: Chat GPT by Open AI
                # Prompt: How can we filter the submitted reviews? 
                filter_name = st.text_input("Filter by name")
                filter_rating = st.slider("Filter by rating", 1, 5, (1, 5), step=1)
                
                # Die gefilterten Bewertungen werden in einer Tabelle angezeigt
                # Source: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state
                filtered_reviews = st.session_state.reviews
                if filter_name:
                    filtered_reviews = filtered_reviews[filtered_reviews['Name'].str.contains(filter_name, case=False)]
                filtered_reviews = filtered_reviews[(filtered_reviews['Rating'] >= filter_rating[0]) & (filtered_reviews['Rating'] <= filter_rating[1])]
                
                st.dataframe(filtered_reviews.drop('Restaurant ID', axis=1))
                coords = pd.DataFrame(columns=['lat', 'lon'])
                for restaurant_id in filtered_reviews['Restaurant ID']:
                    try:
                        # Die gefilterten Restaurants werden auf einer Karte angezeigt
                        # Source: https://docs.streamlit.io/develop/api-reference/charts/st.map
                        restaurant_coords = restaurants_df[restaurants_df['id'] == restaurant_id][['lat', 'lon']].iloc[0]
                        coords.loc[len(coords)] = restaurant_coords
                    except Exception as e:
                        st.write(f"Failed to get coordinates for restaurant ID {restaurant_id}: {e}")
                        continue

                st.map(coords)
        else:
            st.write("No restaurants found in this location.")

# Die main-Funktion wird nur ausgeführt, wenn das Skript direkt aufgerufen wird und nicht, wenn es als Modul importiert wird
if __name__ == "__main__":
    main()
