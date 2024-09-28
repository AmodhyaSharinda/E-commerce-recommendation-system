import streamlit as st
from streamlit_option_menu import option_menu

import home, trending, login, signup

class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        })

    def run(self):
        # Use sidebar for the app menu
        with st.sidebar:        
            app = option_menu(
                menu_title='Pondering',
                options=['Home', 'Login', 'Signup', 'Trending'],
                icons = ['house-fill', 'person-circle', 'person-fill', 'star-fill'],
                menu_icon='chat-text-fill',
                default_index=0,  # Set default index to 0 for Home
                styles={
                    "container": {"padding": "40px", "background-color": 'black', "height": "450px"},
                    "icon": {"color": "white", "font-size": "20px"},
                    "nav-link": {
                        "color": "white",
                        "font-size": "18px",
                        "text-align": "left",
                        "margin": "13px 5px",
                        "--hover-color": "gray",
                    },
                    "nav-link-selected": {"background-color": "#0056b3", "border-radius": "5px"},
                }
            )
        # Logout button
        if st.session_state.get("logged_in"):
            if st.sidebar.button("Logout"):
                self.logout()
                    
        # Call the corresponding app function
        if app == "Home":
            home.app()
        elif app == "Login":
            if st.session_state.get("logged_in"):
                st.success(f"Already logged in as {st.session_state.username}.")
                st.session_state.selected_app = "Home"  # Redirect to Home
                home.app()
            else:
                login.app()   
        elif app == "Trending":
            trending.app()        
        elif app == "Signup":
            signup.app()

    def logout(self):
        # Clear session state for login
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.selected_app = None  # Optionally reset the selected app
        st.success("You have been logged out.")
        st.rerun() 

if __name__ == "__main__":
    app = MultiApp()
    app.run()
