import streamlit as st
import pickle
from PIL import Image
import pandas as pd
import numpy as np
import re

@st.cache_data
def load_product_categories():
    with open("artifacts/Proudct_categories.pkl", 'rb') as file:
        return pickle.load(file)
products_categories = load_product_categories()

@st.cache_data
def load_user_similarity_df():
    with open("artifacts/user_similarity_df.pkl", 'rb') as file:
        return pickle.load(file)
user_similarity_df = load_user_similarity_df()

@st.cache_data
def load_user_item_matrix():
    with open("artifacts/user_item_matrix.pkl", 'rb') as file:
        return pickle.load(file)
user_item_matrix = load_user_item_matrix()

@st.cache_data
def load_item_user_matrix():
    with open("artifacts/item_user_matrix.pkl", 'rb') as file:
        return pickle.load(file)
item_user_matrix = load_item_user_matrix()

@st.cache_data
def load_product():
    with open("artifacts/product.pkl", 'rb') as file:
        return pickle.load(file)
product = load_product()

@st.cache_data
def load_cosine_similarity_matrix():
    with open("artifacts/cosinesimilarity_matrix.pkl", 'rb') as file:
        return pickle.load(file)
cosinesimilarity_matrix = load_cosine_similarity_matrix()

@st.cache_data
def load_item_similarity_df():
    with open("artifacts/item_similarity_df.pkl", 'rb') as file:
        return pickle.load(file)
item_similarity_df = load_item_similarity_df()

@st.cache_data
def save_data(data):
    with open("artifacts/data.pkl", 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

@st.cache_data
# def load_rules():
#     with open("artifacts/rules.pkl", 'rb') as file:
#         return pickle.load(file)
# rules = load_rules()

@st.cache_data
def load_dataset():
    with open("artifacts/dataset.pkl", 'rb') as file:
        return pickle.load(file)
dataset = load_dataset()



def recommend_similar_products(product_name, category, top_n):
    # # Check if product_name and category are valid strings
    # if not isinstance(product_name, str) or not isinstance(category, str):
    #     st.error("Product name and category must be valid strings.")
    #     return []

    # Debugging output
    print(f"Searching for Product Name: '{product_name}', Category: '{category}'")

    # Handle NaN values in DataFrame columns
    #product['product_title'] = product['product_title'].fillna('')
    #product['category'] = product['category'].fillna('')

    product_df = pd.read_pickle('artifacts/product.pkl')

    product_titles = product_df['product_title']  # Change 'product_title' to your actual column name

    # Perform the search allowing for any token match
    product_indices = product_df[product_df['product_title'].str.contains(product_name, case=False, na=False) &
                                 product_df['category'].str.contains(category, case=False, na=False)].index


    print(product_indices)
        
    if len(product_indices) == 0:
        st.error(f"No product found matching '{product_name}' in the dataset.")
        return []
        
    product_index = product_indices[0]
    distances = cosinesimilarity_matrix[product_index]
    similar_products_indices = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:top_n + 1]

    recommended_products = []
    for i in similar_products_indices:
        recommended_product = product.iloc[i[0]]
        recommended_products.append(recommended_product['product_title'])

    return recommended_products

def get_user_recommendations(user_id, n_recommendations):
        similar_users = user_similarity_df[user_id].sort_values(ascending=False).index[1:]  # Exclude self
        recommendations = []

        for similar_user in similar_users:
            recommended_items = user_item_matrix.loc[similar_user][user_item_matrix.loc[similar_user] > 0].index
            recommendations.extend(recommended_items)

        # Filter already purchased items
        recommendations = set(recommendations) - set(user_item_matrix.loc[user_id][user_item_matrix.loc[user_id] > 0].index)
        return list(recommendations)[:n_recommendations]

def get_item_based_recommendations(user_id, n_recommendations):
    
    if user_id not in item_user_matrix.columns:
        st.error(f"No user found with ID '{user_id}'.")
        return []

    user_items = item_user_matrix.loc[:, user_id]
    interacted_items = user_items[user_items > 0].index
    item_scores = {}

    for item in interacted_items:
        similar_items = item_similarity_df[item].sort_values(ascending=False)[1:]
        for similar_item, score in similar_items.items():
            if similar_item not in interacted_items:
                item_scores[similar_item] = item_scores.get(similar_item, 0) + score

    recommended_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)
    return [item[0] for item in recommended_items][:n_recommendations]

# def apriori_recommendations(items, top_n):
#         recommendations = {}
#         for item in items:
#             rule_subset = rules[rules['antecedents'].apply(lambda x: item in x)]
#             for consequent in rule_subset['consequents']:
#                 recommendations[consequent] = recommendations.get(consequent, 0) + 1

#         return pd.Series(recommendations).sort_values(ascending=False).head(top_n)

def hybrid_recommendation(user, product_title, category, no_of_recommendations, w_user_user=0.1, w_item_item=0.3, w_content=0.4, w_rule=0.2):
        user_user_score = get_user_recommendations(user, no_of_recommendations)
        item_item_score = get_item_based_recommendations(user, no_of_recommendations)
        content_score = recommend_similar_products(product_title, category, no_of_recommendations)
        # if isinstance(content_score, str):  # Check if it's a string
        #     content_score = [content_score]  # Convert it to a list
        # else:
        #     content_score = [rec['title'] for rec in content_score]  # Process as before

        #apirori_rule_score = apriori_recommendations(content_score, no_of_recommendations)

        final_recommendations = []
        for item in set(user_user_score + item_item_score + content_score ):
            score = (
                (item in user_user_score) * w_user_user +
                (item in item_item_score) * w_item_item +
                (item in content_score) * w_content 
            )
            if is_item_in_category(item, category):
                final_recommendations.append((item, score))

        final_recommendations.sort(key=lambda x: x[1], reverse=True)
        print(final_recommendations)
        return final_recommendations[:no_of_recommendations]

def get_image_url_by_title(title):
    product_row = product[product['product_title']== title]
    return product_row.iloc[0]['image'] if not product_row.empty else None

def is_item_in_category(item, category):
    print(f"Searching for item: '{item}'")  # Debugging output

        # Check if item is in any product title
    item_in_titles = dataset['product_title'].str.contains(r'\b' + re.escape(item) + r'\b', case=False, na=False)

    if item_in_titles.any():
        print("Item found in titles.")  # Debugging output
        # If item found in titles, retrieve the corresponding categories
        matched_categories = dataset.loc[item_in_titles, 'category'].unique()
        matched_categories_lower = [cat.lower() for cat in matched_categories]  # Convert to lowercase
        print(f"Matched categories: {matched_categories}")  # Debugging output

        result = category.lower() in matched_categories_lower  # Case-insensitive match
        print(f"Category match result: {result}")  # Debugging output
        return result  # Return True if the category matches any found

    st.write("Item not found in titles.")  # Debugging output
    return False  # Return False if no match is found

def app():
    # Lazy loading of data on button click
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    st.title("🛍️ E-commerce Recommendation System")

    # Search for items
    searched_product = st.text_input("🔍 Search for items:")
    if searched_product:
        st.write(f"You searched for: **{searched_product}**")

    # Select product category
    selected_product_category = st.selectbox("📦 Select category from dropdown", products_categories)


    if st.button("✨ Show Recommendations"):

        if not st.session_state.data_loaded:
            # Load data
            st.session_state.user_similarity_df = load_user_similarity_df()
            st.session_state.user_item_matrix = load_user_item_matrix()
            st.session_state.product = load_product()
            st.session_state.cosinesimilarity_matrix = load_cosine_similarity_matrix()
            st.session_state.item_similarity_df = load_item_similarity_df()
            #st.session_state.rules = load_rules()
            st.session_state.dataset = load_dataset()
            st.session_state.data_loaded = True
        
        # Define the number of recommendations
        no_of_recommendations = 10
        if 'logged_in' in st.session_state and st.session_state.logged_in:
            no_of_hybridRecs = 10
            
            if st.session_state.username in user_similarity_df.index:
                hybridRecs = hybrid_recommendation(st.session_state.username, searched_product, selected_product_category, no_of_hybridRecs)
                print(hybridRecs)
                if hybridRecs:
                    # Split the products for two rows
                    first_row_products = hybridRecs[:5]  # First 5 products
                    second_row_products = hybridRecs[5:10]  # Next 5 products if available
                        
                    if first_row_products: 
                        print(first_row_products)   # Display first row
                        row1_cols = st.columns(5)
                        for i, Rec_product in enumerate(first_row_products):
                            image_url = get_image_url_by_title(Rec_product[0])
                            if image_url:
                                with row1_cols[i]:
                                    image_url = get_image_url_by_title(Rec_product[0])
                                    st.markdown(
                                        f"""
                                        <div style="text-align:center; border: 3px solid #e6e6e6; border-radius: 10px; padding: 30px;">
                                            <a href='#' target='_blank'>
                                                <img src="{image_url}" alt="{Rec_product}" style="width:100%;">
                                                <h11 style="margin-top:10px; color:white;">{Rec_product}</h11>
                                            </a>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )    

                        # Display second row
                    if second_row_products:
                        row2_cols = st.columns(5)
                        for i, Rec_product in enumerate(second_row_products):
                            image_url = get_image_url_by_title(Rec_product[0])
                            if image_url:
                                with row2_cols[i]:
                                    image_url = get_image_url_by_title(Rec_product[0])
                                    st.markdown(
                                        f"""
                                        <div style="text-align:center; border: 3px solid #e6e6e6; border-radius: 10px; padding: 30px;">
                                            <a href='#' target='_blank'>
                                                <img src="{image_url}" alt="{Rec_product}" style="width:100%;">
                                                <h11 style="margin-top:10px; color:white;">{Rec_product}</h11>
                                            </a>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )    
                else:
                    st.error("No hybrid Recomandations found.")
                    st.success("Recomendations Based on search (Content Based).")
                    recommendations = recommend_similar_products(searched_product, selected_product_category, no_of_recommendations)

                    if recommendations:
                        # Split the products for two rows
                        first_row_products = recommendations[:5]  # First 5 products
                        second_row_products = recommendations[5:10]  # Next 5 products if available
                            
                        if first_row_products: 
                            print(first_row_products)   # Display first row
                            row1_cols = st.columns(5)
                            for i, Rec_product in enumerate(first_row_products):
                                image_url = get_image_url_by_title(Rec_product)
                                if image_url:
                                    with row1_cols[i]:
                                        image_url = get_image_url_by_title(Rec_product)
                                        st.markdown(
                                            f"""
                                            <div style="text-align:center; border: 3px solid #e6e6e6; border-radius: 10px; padding: 30px;">
                                                <a href='#' target='_blank'>
                                                    <img src="{image_url}" alt="{Rec_product}" style="width:100%;">
                                                    <h11 style="margin-top:10px; color:white;">{Rec_product}</h11>
                                                </a>
                                            </div>
                                            """,
                                            unsafe_allow_html=True
                                        )    

                            # Display second row
                        if second_row_products:
                            row2_cols = st.columns(5)
                            for i, Rec_product in enumerate(second_row_products):
                                image_url = get_image_url_by_title(Rec_product)
                                if image_url:
                                    with row2_cols[i]:
                                        image_url = get_image_url_by_title(Rec_product)
                                        st.markdown(
                                            f"""
                                            <div style="text-align:center; border: 3px solid #e6e6e6; border-radius: 10px; padding: 30px;">
                                                <a href='#' target='_blank'>
                                                    <img src="{image_url}" alt="{Rec_product}" style="width:100%;">
                                                    <h11 style="margin-top:10px; color:white;">{Rec_product}</h11>
                                                </a>
                                            </div>
                                            """,
                                            unsafe_allow_html=True
                                        )
            else:
                st.success("Recomendations Based on search (Content Based).")
                recommendations = recommend_similar_products(searched_product, selected_product_category, no_of_recommendations)

                if recommendations:
                    # Split the products for two rows
                    first_row_products = recommendations[:5]  # First 5 products
                    second_row_products = recommendations[5:10]  # Next 5 products if available
                            
                    if first_row_products: 
                        print(first_row_products)   # Display first row
                        row1_cols = st.columns(5)
                        for i, Rec_product in enumerate(first_row_products):
                            image_url = get_image_url_by_title(Rec_product)
                            if image_url:
                                with row1_cols[i]:
                                    image_url = get_image_url_by_title(Rec_product)
                                    st.markdown(
                                        f"""
                                        <div style="text-align:center; border: 3px solid #e6e6e6; border-radius: 10px; padding: 30px;">
                                            <a href='#' target='_blank'>
                                                <img src="{image_url}" alt="{Rec_product}" style="width:100%;">
                                                <h11 style="margin-top:10px; color:white;">{Rec_product}</h11>
                                            </a>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )    

                            # Display second row
                    if second_row_products:
                        row2_cols = st.columns(5)
                        for i, Rec_product in enumerate(second_row_products):
                            image_url = get_image_url_by_title(Rec_product)
                            if image_url:
                                with row2_cols[i]:
                                    image_url = get_image_url_by_title(Rec_product)
                                    st.markdown(
                                        f"""
                                        <div style="text-align:center; border: 3px solid #e6e6e6; border-radius: 10px; padding: 30px;">
                                            <a href='#' target='_blank'>
                                                <img src="{image_url}" alt="{Rec_product}" style="width:100%;">
                                                <h11 style="margin-top:10px; color:white;">{Rec_product}</h11>
                                            </a>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )    
                
        else:
            recommendations = recommend_similar_products(searched_product, selected_product_category, no_of_recommendations)

            if recommendations:
                # Split the products for two rows
                first_row_products = recommendations[:5]  # First 5 products
                second_row_products = recommendations[5:10]  # Next 5 products if available
                    
                if first_row_products: 
                    print(first_row_products)   # Display first row
                    row1_cols = st.columns(5)
                    for i, Rec_product in enumerate(first_row_products):
                        image_url = get_image_url_by_title(Rec_product)
                        if image_url:
                            with row1_cols[i]:
                                image_url = get_image_url_by_title(Rec_product)
                                st.markdown(
                                    f"""
                                    <div style="text-align:center; border: 3px solid #e6e6e6; border-radius: 10px; padding: 30px;">
                                        <a href='#' target='_blank'>
                                            <img src="{image_url}" alt="{Rec_product}" style="width:100%;">
                                            <h11 style="margin-top:10px; color:white;">{Rec_product}</h11>
                                        </a>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )    

                    # Display second row
                if second_row_products:
                    row2_cols = st.columns(5)
                    for i, Rec_product in enumerate(second_row_products):
                        image_url = get_image_url_by_title(Rec_product)
                        if image_url:
                            with row2_cols[i]:
                                image_url = get_image_url_by_title(Rec_product)
                                st.markdown(
                                    f"""
                                    <div style="text-align:center; border: 3px solid #e6e6e6; border-radius: 10px; padding: 30px;">
                                        <a href='#' target='_blank'>
                                            <img src="{image_url}" alt="{Rec_product}" style="width:100%;">
                                            <h11 style="margin-top:10px; color:white;">{Rec_product}</h11>
                                        </a>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )    
            
            else:
                st.write("No recommendations found.")
