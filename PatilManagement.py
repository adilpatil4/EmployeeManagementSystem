#
#  PatilManagement.py
#  EmployeeDetails
#
#  Created by Adil Patil on 10/1/24.
#

import streamlit as st
import mysql.connector
import re
import sys

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #FFFFFF; /* Background Color */
    }
    .logout-button {
        background-color: #FF6F61; /* Primary Color */
        color: #FFFFFF; /* White text for contrast */
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        cursor: pointer;
        transition: background-color 0.3s;
        position: absolute;
        top: 20px;
        right: 20px;
        z-index: 1000; /* Ensure button is on top */
    }
    .logout-button:hover {
        background-color: #FF8A65; /* Lighter Coral on hover */
    }
    .stButton > button {
        background-color: #FF6F61; /* Primary Color */
        color: #FFFFFF; /* White text for contrast */
        font-size: 16px;
        margin: 10px 0;
        border-radius: 5px;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #FF8A65; /* Lighter Coral on hover */
    }
    .stTextInput input, .stNumberInput input {
        background-color: #F7F7F7; /* Secondary Background Color */
        color: #333333; /* Text Color */
        font-size: 14px;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #CCCCCC; /* Light gray border */
    }
    .stTextInput input:focus {
        border-color: #FF6F61; /* Primary Color on focus */
        box-shadow: 0 0 5px rgba(255, 111, 97, 0.5);
    }
    .stMarkdown {
        color: #333333; /* Text Color */
    }
    </style>
""", unsafe_allow_html=True)


# Utility functions
def finish_with_error(error):
    st.error(f"Error: {error}")
    sys.exit(1)


def connect_to_database():
    try:
        con = mysql.connector.connect(
            user='root',
            password='AdilSahil786',
            host='localhost',
            database='company_db'
        )
        return con
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None


def validate_ssn_format(ssn):
    if len(ssn) == 9 and ssn.isdigit():
        return True
    elif len(ssn) == 11 and ssn[3] == '-' and ssn[6] == '-' and all(
            c.isdigit() for i, c in enumerate(ssn) if i != 3 and i != 6):
        return True
    return False


def format_ssn(ssn):
    if len(ssn) == 9:
        return f"{ssn[:3]}-{ssn[3:5]}-{ssn[5:]}"
    return ssn


def validate_email_format(email):
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email) is not None


# Database interaction functions
def fetch_employee_details(con, ssn):
    cursor = con.cursor()
    query = "SELECT ssn, first_name, last_name, email, city, balance FROM employees WHERE ssn = %s"
    cursor.execute(query, (ssn,))
    row = cursor.fetchone()

    if not row:
        st.warning(f"No employee found with SSN: {ssn}")
    else:
        st.subheader(f"Employee Details for {row[1]} {row[2]}")
        st.write("-------------------------------")
        st.write(f"**SSN:** {row[0]}")
        st.write(f"**First Name:** {row[1]}")
        st.write(f"**Last Name:** {row[2]}")
        st.write(f"**Email:** {row[3]}")
        st.write(f"**City:** {row[4]}")
        st.write(f"**Balance:** ${row[5]}")
        st.write("-------------------------------")

    cursor.close()


def update_employee_details(con):
    cursor = con.cursor()

    # Ensure SSN is stored in session state
    if 'ssn' not in st.session_state:
        st.session_state.ssn = ""

    # Input for SSN
    ssn_input = st.text_input("Enter the employee's SSN:", st.session_state.ssn)
    st.session_state.ssn = ssn_input  # Store the SSN in session state

    # Radio button for selection
    choice = st.radio("Select detail to update:", ["Last Name", "Email", "City"], key="update_choice")

    # Update value field
    new_value = st.text_input(f"Enter new {choice}:", "")

    if st.button("Update Details"):
        if ssn_input and validate_ssn_format(ssn_input):
            if choice == "Email" and not validate_email_format(new_value):
                st.warning("Invalid email format. Update failed.")
                return

            # Initialize column_name to None
            column_name = None

            # Assign the correct column name based on the choice
            if choice == "Last Name":
                column_name = "last_name"  # Adjust to match the actual database column name
            elif choice == "Email":
                column_name = "email"
            elif choice == "City":
                column_name = "city"

            # Check if column_name is defined before proceeding
            if column_name is not None:
                query = f"UPDATE employees SET {column_name} = %s WHERE ssn = %s"
                try:
                    cursor.execute(query, (new_value, format_ssn(ssn_input)))
                    con.commit()
                    st.success(f"{choice} updated successfully.")
                except mysql.connector.Error as err:
                    finish_with_error(err)
            else:
                st.error("No valid column selected for update.")

    cursor.close()


def transfer_funds(con):
    cursor = con.cursor()

    from_ssn = st.text_input("SSN to transfer FROM (format XXX-XX-XXXX):")
    to_ssn = st.text_input("SSN to transfer TO (format XXX-XX-XXXX):")
    amount = st.number_input("Amount to transfer:", min_value=0)

    if st.button("Transfer Funds"):
        if not validate_ssn_format(from_ssn) or not validate_ssn_format(to_ssn):
            st.warning("Invalid SSN format.")
            return

        from_ssn = format_ssn(from_ssn)
        to_ssn = format_ssn(to_ssn)

        # Ensure that the amount is greater than 0
        if amount <= 0:
            st.warning("Please enter an amount greater than 0.")
            return

        # Implement the fund transfer logic here (e.g., checking balances and updating records)
        # For simplicity, we'll just show a success message for now.
        st.success(f"Transferred ${amount} from {from_ssn} to {to_ssn}.")

    cursor.close()

def main():
    st.title("Patil Employee Management System")

    if 'password_verified' not in st.session_state:
        st.session_state.password_verified = False

    # Logout logic
    if 'logout' in st.session_state and st.session_state.logout:
        st.session_state.password_verified = False
        st.session_state.ssn = ""  # Clear the stored SSN
        st.session_state.password_input = ""  # Clear password input
        st.session_state.logout = False

    if st.session_state.password_verified:
        # Show logout button
        st.button("Logout", on_click=lambda: st.session_state.update({"logout": True}), key="logout_button")

        # Main Menu
        option = st.selectbox(
            "Choose an action:",
            ["Select an option", "View Employee Details", "Update Employee Details", "Transfer Funds"]
        )

        if option == "View Employee Details":
            ssn = st.text_input("Enter the employee's SSN:", key="view_ssn")
            if st.button("View Details"):
                if ssn and validate_ssn_format(ssn):
                    con = connect_to_database()
                    if con:
                        fetch_employee_details(con, format_ssn(ssn))

        elif option == "Update Employee Details":
            con = connect_to_database()
            if con:
                update_employee_details(con)

        elif option == "Transfer Funds":
            con = connect_to_database()
            if con:
                transfer_funds(con)

    else:
        def verify_password():
            password = st.session_state.password_input
            correct_password = "AdilSahil786"
            if password == correct_password:
                st.session_state.password_verified = True
                st.success("Password verified. You may proceed.")
            else:
                st.error("Incorrect password. Please try again.")

        st.text_input("Enter MySQL password to proceed:", type="password", key="password_input", on_change=verify_password)

if __name__ == "__main__":
    main()
