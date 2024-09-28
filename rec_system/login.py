import streamlit as st
import main
from auth import collection, hash_password

def app():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = collection.find_one({"user_id": username})
        #st.write(user)
        if user and (user["password"] == hash_password(password) or user["password"] == password):
            st.session_state.logged_in = True  # Set the login state
            st.session_state.username = username # Store the username
            #st.session_state.selected_app = "Home" 
            st.success(f"Welcome back, {username}!")
            st.rerun()  # Rerun to refresh the app
        else:
            st.error("Invalid username or password.")
