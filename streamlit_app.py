mport streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, db
import pandas as pd

# Check if Firebase app is already initialized
if not firebase_admin._apps:
    # Initialize Firebase only if it hasn't been done already
    cred = credentials.Certificate(r"C:\Users\ns117\Downloads\shaped-gravity-410717-firebase-adminsdk-pizxu-19a1d865dd.json")
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://shaped-gravity-410717-default-rtdb.asia-southeast1.firebasedatabase.app/'})

# Function for user login
def login():
    st.header("Login")
    email = st.text_input("Enter your email:", key="login_email")  # Provide a unique key
    password = st.text_input("Enter your password:", type="password", key="login_password")  # Provide a unique key

    if st.button("Login"):
        try:
            user = auth.get_user_by_email(email)
            # Placeholder for custom login logic
            st.session_state.is_logged_in = True  # Set the login state to True
            st.session_state.user_name = user.display_name  # Store user's name in session state
            st.success("Login successful!")
        except auth.UserNotFoundError:
            st.error("User not found. Please check your email.")
        except Exception as e:
            st.error(f"Login failed. Error: {e}")

# Function for user signup
def signup():
    st.header("Sign up")
    email = st.text_input("Enter your email:", key="signup_email")  # Provide a unique key
    password = st.text_input("Enter your password:", type="password", key="signup_password")  # Provide a unique key
    re_password = st.text_input("Re-Enter your password:", type="password", key="signup_re_password")  # Provide a unique key
    name = st.text_input("Enter your name:", key="signup_name")  # Provide a unique key

    if password == re_password:
        if st.button("Sign up"):
            try:
                user = auth.create_user(
                    email=email,
                    password=password,
                    display_name=name  # Set user's name during signup
                )
                auth.update_user(
                    user.uid,
                    email_verified=False
                )
                st.success("User created successfully")
            except firebase_admin.auth.EmailAlreadyExistsError:
                st.error("Email already exists")
    else:
        st.error("The passwords you entered do not match")

# Function for resetting password
def forgot_password():
    st.header("Forgot Password")
    email = st.text_input("Enter your email:", key="forgot_password_email")  # Provide a unique key

    if st.button("Reset Password"):
        try:
            auth.send_password_reset_email(email)
            st.success("Password reset email sent. Check your inbox.")
        except auth.UserNotFoundError:
            st.error("User not found. Please check your email.")
        except Exception as e:
            st.error(f"Failed to send reset email. Error: {e}")

# Function to show and download entries
def show_entries():
    st.title("Show Entries")
    user_name = st.session_state.user_name

    # Retrieve user's entries from Firebase Realtime Database
    entries_ref = db.reference('accounting_data')
    entries_data = entries_ref.get()

    if entries_data:
        user_entries = [entry for entry in entries_data.values() if entry.get('user_name') == user_name]

        if user_entries:
            # Display entries
            st.write("Your Entries:")
            df_entries = pd.DataFrame(user_entries)
            st.dataframe(df_entries)

            # Download entries as CSV
            csv_file = df_entries.to_csv(index=False)
            st.download_button(label="Download Entries as CSV", data=csv_file, file_name=f"{user_name}_entries.csv", key="download_csv_button")
        else:
            st.info("No entries found for the user.")
    else:
        st.info("No entries found in the database.")

# Main accounting page
def accounting_page():
    # Title and user information
    st.title("Accounting Page")
    # Check if username is available in session state and handle accordingly
    if "user_name" not in st.session_state:
        st.error("Please login to proceed with accounting.")
        # Alternatively, provide login functionality within this page
        return

    # Input fields with improved logic
    remarks = st.text_input("Enter remarks:", key="remarks", max_chars=255)
    # Additional validation for amount:
    amount = st.number_input("Enter amount:", key="amount", min_value=0)
    date_value = st.date_input("Select date:", key="date")
    time_value = st.time_input("Select time:", key="time")
    reason = st.text_input("Enter reason:", key="reason", max_chars=255)
    reimbursement = st.radio("Reimbursement:", ["Yes", "No"], key="reimbursement")

    # Processing logic
    if st.button("Submit", disabled= not all([remarks, amount, date_value, reason])):
        data = {
            "user_name": st.session_state["user_name"],
            "remarks": remarks,
            "amount": amount,
            "date": str(date_value),
            "time": str(time_value),
            "reason": reason,
            "reimbursement": reimbursement,
        }

        try:
            # push data to firebase
            db.reference("accounting_data").push(data)
            st.success(" Credentials submitted. Data stored in firebase.")
        except Exception as e:
            # Handle firebase errors gracefully
            st.error(f"Error submitting data: {e}")

# Streamlit app
def main():
    st.title("Firebase Authentication App")

    # Initialize session state
    if 'is_logged_in' not in st.session_state:
        st.session_state.is_logged_in = False

    option = st.radio("Choose an option", ["Login", "Sign Up", "Forgot Password"])

    if option == "Login":
        login()
    elif option == "Sign Up":
        signup()
    elif option == "Forgot Password":
        forgot_password()

    # Redirect to accounting page if logged in
    if st.session_state.is_logged_in:
        accounting_page()

    # Show entries option
    if st.session_state.is_logged_in:
        show_entries()

if __name__ == "__main__":
    main()
