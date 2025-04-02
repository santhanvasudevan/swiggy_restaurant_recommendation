import streamlit as st
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix

# Set full-screen width
st.set_page_config(layout="wide")

# Load datasets without index
cleaneddata_df = pd.read_csv(r"data\cleaned_data.csv", index_col=False)
encoded_df = pd.read_csv(r"data\encoded_data.csv", index_col=False)

# Ensure index is reset
cleaneddata_df.reset_index(drop=True, inplace=True)
encoded_df.reset_index(drop=True, inplace=True)

# Convert cuisine column to string for proper display
cleaneddata_df["cuisine"] = cleaneddata_df["cuisine"].astype(str)

# Convert to sparse format for memory efficiency
sparse_matrix = csr_matrix(encoded_df.values)

# Initialize NearestNeighbors model
nn = NearestNeighbors(n_neighbors=6, metric='cosine', algorithm='brute')
nn.fit(sparse_matrix)

def get_similar_restaurants(index, top_n=5):
    """Get top N most similar restaurants using Nearest Neighbors."""
    distances, indices = nn.kneighbors(sparse_matrix[index].reshape(1, -1))
    top_indices = indices[0][1:top_n+1]  # Exclude selected restaurant
    return cleaneddata_df.iloc[top_indices]

# Streamlit UI
st.title("🍽 Restaurant Recommendation System")

# Display full restaurant list as an interactive table
st.subheader("Select a Restaurant")
st.dataframe(cleaneddata_df[['name', 'city', 'rating', 'rating_count', 'cost', 'cuisine']], use_container_width=True)

# Searchable input field to filter restaurants
search_query = st.text_input("🔎 Search for a restaurant")

# Filter dropdown options based on user input
filtered_restaurants = cleaneddata_df[cleaneddata_df["name"].str.contains(search_query, case=False, na=False)]

# Dropdown to select a restaurant (after filtering)
selected_restaurant = st.selectbox("Choose a restaurant for recommendations", filtered_restaurants['name'].tolist())

if selected_restaurant:
    # Get index of selected restaurant
    selected_index = cleaneddata_df[cleaneddata_df['name'] == selected_restaurant].index[0]

    # Show selected restaurant details
    st.write("### 🎯 Selected Restaurant")
    st.dataframe(cleaneddata_df.iloc[[selected_index]])

    # Get recommendations
    recommended_restaurants = get_similar_restaurants(selected_index)

    # Display recommendations
    st.write("### ⭐ Recommended Restaurants to Try")
    st.dataframe(recommended_restaurants)