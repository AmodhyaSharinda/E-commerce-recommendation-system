import streamlit as st
from auth import collection, hash_password

def app():
    st.title("Sign Up")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):
        if collection.find_one({"user_id": username}):
            st.error("Username already exists!")
        else:
            hashed_pw = hash_password(password)
            collection.insert_one({"user_id": username, "password": hashed_pw})
            st.success("Account created successfully!")
