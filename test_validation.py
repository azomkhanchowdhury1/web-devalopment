
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

validator = UnicodeUsernameValidator()
username = "a@gmail.com"

try:
    validator(username)
    print(f"'{username}' is valid.")
except ValidationError as e:
    print(f"'{username}' is INVALID: {e}")

username_with_space = "a@gmail.com "
try:
    validator(username_with_space)
    print(f"'{username_with_space}' is valid.")
except ValidationError as e:
    print(f"'{username_with_space}' is INVALID: {e}")
