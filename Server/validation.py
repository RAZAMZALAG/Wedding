from flask import jsonify
import re

# sapir for commit
def is_valid_username(username):
    # Does not begin and end with blank, Only English and Hebrew letters, Between 2 and 15 letters
    pattern = r"^(?! )[a-zA-Zא-ת0-9_ ]{2,15}(?<! )$"
    if not re.match(pattern, username):
        return jsonify({"error": 'FIRST_NAME_NOT_VALID'}), 400
    #  Maximum 3 spaces
    if username.count(" ") > 3:
        return jsonify({"error": 'FIRST_NAME_MUST_CONTAIN_LESS_THAN_3_SPACES'}), 400
    username = username.lower()
    # DOES NOT HAVE MORE THAN 3 REPEATED CHARACTERS
    if re.search(r"(.)\1{3,}", username):
        return jsonify({"error": 'FIRST_NAME_MUST_NOT_CONTAIN_MORE_THAN_3_REPETITIONS'}), 400
    # If all checks passed
    return None  # None means no errors


def is_valid_phone(phone):
    #  Must start with 0 or +972, and contain a total of 9 digits (7 digits after the prefix)
    pattern = r"^(\+972|0)([23489]|5[0-9])\d{7}$"
    # If all checks passed
    if not re.match(pattern, phone):
        return jsonify({"error": 'PHONE_NUMBER_ILLEGAL'}), 400
    # If all checks passed
    return None


def is_valid_email(email):
    # 1. Local part (before @): allows letters, digits, and special characters like ., _, %, +, -
    # 2. @: separates the local part from the domain
    # 3. Domain name (after @): allows letters, digits, dashes, and dots
    # 4. TLD (Top Level Domain): must be at least 2 characters long, e.g., .com, .org
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return jsonify({"error": 'EMAIL_ILLEGAL'}), 400
    # If the email is valid, return None (indicating no errors)
    return None


def is_valid_password(password):
    # check the length of the password
    if len(password) > 10 or len(password) < 5:
        return {"error": "PASSWORD_LENGTH_MUST_BE_BETWEEN_5_AND_10_CHARACTERS"}, 400

    # PASSWORD MUST START WITH AN UPPERCASE LETTER
    if not re.match(r"^[A-Z]", password):
        return {"error": "PASSWORD_MUST_START_WITH_AN_UPPERCASE_LETTER"}, 400

    if not re.search(r"[a-z]", password):
        return {"error": "PASSWORD_MUST_CONTAIN_AT_LEAST_ONE_LOWERCASE_LETTER"}, 400

    # PASSWORD MUST CONTAIN AT LEAST ONE DIGIT
    if not re.search(r"[0-9]", password):
        return {"error": "PASSWORD_MUST_CONTAIN_AT_LEAST_ONE_DIGIT"}, 400

    # PASSWORD MUST CONTAIN AT LEAST ONE SPECIAL CHARACTER
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return {"error": "PASSWORD_MUST_CONTAIN_AT_LEAST_ONE_SPECIAL_CHARACTER"}, 400

    # PASSWORD MUST NOT CONTAIN SPACES
    if re.search(r"\s", password):
        return {"error": "PASSWORD_MUST_NOT_CONTAIN_SPACES"}, 400

    # PASSWORD_IS_VALID
    return None


def is_valid_location(location):
    if location not in ["הדר", "לא מחיפה", "מחיפה, לא מהדר"]:
        return {"error": "INVALID_LOCATION"}, 400
    return None


def validate_registration(first_name, last_name, phone, email, location, agreement, password):
    # Validate the username
    if not first_name:
        return jsonify({"error": 'FIRST_NAME_REQUIRED'}), 400
    error = is_valid_username(first_name)
    if error:
        # Return the error message if validation failed
        return error

    # Validate the last name
    if not last_name:
        return jsonify({"error": 'LAST_NAME_REQUIRED'}), 400

    error = is_valid_username(last_name)
    if error:
        return error

    # validate the phone number
    if not phone:
        return jsonify({"error": 'PHONE_NUMBER_REQUIRED'}), 400
    error = is_valid_phone(phone)
    if error:
        return error

    # validate the mail Email address
    if not email:
        return jsonify({"error": 'EMAIL_REQUIRED'}), 400

    error = is_valid_email(email)
    if error:
        return error

    # validate location dropdown
    if not location:
        return jsonify({"error": 'LOCATION_REQUIRED'}), 400
    error = is_valid_location(location)
    if error:
        return error

    if not agreement:
        return jsonify({"error": 'YOU_MUST_AGREE_TO_THE_TERMS_OF_USE'}), 400

    # validate password
    if not password:
        return jsonify({'error': 'PASSWORD_REQUIRED'}), 400
    error = is_valid_password(password)
    if not error:
        return error

def is_valid_permission(value):
    try:
        value = int(value)
        if value in [1, 2]:
            return None
        return jsonify({'error': 'INVALID_PERMISSION'}), 400
    except Exception:
        return jsonify({'error': 'INVALID_PERMISSION'}), 400