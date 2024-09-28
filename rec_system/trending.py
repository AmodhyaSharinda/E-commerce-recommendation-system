import streamlit as st
from auth import product_collection
import pandas as pd

def app():
    # Fetch products from MongoDB
    products = list(product_collection.find())

    # Convert products to DataFrame
    products_df = pd.DataFrame(products)

    # Define 'trending' products (e.g., based on review count or rating)
    # In this example, we assume trending products have a high review count and rating
    trending_products = products_df.sort_values(by=['review_count', 'rating'], ascending=False).head(10)

    # Display trending products in Streamlit
    st.title("👜Trending Products", anchor=None)

    def get_image_url_by_title(title):
        product_row = products_df[products_df['product_title'] == title]
        return product_row.iloc[0]['image'] if not product_row.empty else None

    # Container for multiple rows
    container_html_start = """
    <div style="display: flex; flex-wrap: wrap; gap: 20px;">
    """
    container_html_end = "</div>"

    # Initialize the container
    st.markdown(container_html_start, unsafe_allow_html=True)

    for _, row in trending_products.iterrows():
        image_url = get_image_url_by_title(row['product_title'])
        
        # HTML Card Layout with centered image and two items per row using flexbox
        card_html = f"""
        <div style="flex: 1 1 45%; border: 1px solid #e6e6e6; border-radius: 10px; padding: 15px; 
                    margin-bottom: 15px; box-shadow: 2px 2px 12px rgba(0,0,0,0.1); 
                    display: flex; flex-direction: column; align-items: center; text-align: center;">
            <img src="{image_url}" width="150" style="border-radius: 5px; margin-bottom: 10px;">
            <h3 style="margin: 0;">{row['product_title']}</h3>
            <p><strong>Review Count: </strong> {row['review_count']}</p>
            <p><strong>Rating: </strong> {row['rating']}</p>
            <p><strong>Availability: </strong> {row['availability_status']}</p>
        </div>
        """
        
        # Display each card
        st.markdown(card_html, unsafe_allow_html=True)

    # Close the container
    st.markdown(container_html_end, unsafe_allow_html=True)