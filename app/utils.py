import hashlib
import datetime

# Function to hash a password using SHA-256
def hash_password(password):
    # Create a new SHA-256 hash object
    hash_algorithm = hashlib.sha256()
    
    # Update the hash object with the UTF-8 encoded password
    hash_algorithm.update(password.encode('utf-8'))
    
    # Get the hexadecimal representation of the hashed password
    hashed_password = hash_algorithm.hexdigest()
    
    # Return the hashed password
    return hashed_password


# Function to check if entered password matches the stored hashed password
def check_password_hash(stored_hashed_password, entered_password):
    # Hash the entered password and compare with the stored hashed password
    return hash_password(entered_password) == stored_hashed_password


# Function to check if a date string has a valid format (YYYY-MM-DD)
def is_valid_date(date_string):
    try:
        # Attempt to parse the date string using the specified format
        datetime.datetime.strptime(date_string, "%Y-%m-%d")
        return True  # Return True if parsing is successful
    except ValueError:
        return False  # Return False if parsing fails
