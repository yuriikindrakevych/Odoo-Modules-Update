CHARS_TO_DELETE = ";_ "


def get_formatted_email(email):
    if not email:
        return False
    delete_map = str.maketrans("", "", CHARS_TO_DELETE)
    return email.translate(delete_map)
