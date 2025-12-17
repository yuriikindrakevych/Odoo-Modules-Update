try:
    import phonenumbers
    from phonenumbers import PhoneNumberFormat
except ImportError:
    phonenumbers = None


def get_phonenumber_object(number, country=None, company=None):
    """
    Utility function to safely parse a phone number string.

    :param number: The phone number string to parse.
    :param country: A recordset of res.country, used as a region hint.
    :param company: A recordset of res.company, used as a fallback for the country.
    :return: A phonenumbers object if parsing is successful, otherwise None.
    """
    if not number or not phonenumbers:
        return None
    try:
        country_code = country.code if country else None
        if not country_code and company and company.country_id:
            country_code = company.country_id.code

        return phonenumbers.parse(number, region=country_code)
    except Exception:
        return None


def get_national_significant(number, country=None, company=None):
    """
        Function that returns the national significant part of a number.
        If parsing fails, it returns the original number.

        :param number: The phone number string to process.
        :param country: A recordset of res.country.
        :param company: A recordset of res.company.
        :return: The national significant number as a string, or the cleaned original number if it cannot be parsed.
    """
    if not number:
        return False

    cleaned_number = ''.join(filter(lambda c: c in "+0123456789", str(number)))

    if not phonenumbers:
        return cleaned_number

    phone_nbr_obj = get_phonenumber_object(cleaned_number, country, company)
    if phone_nbr_obj and phonenumbers.is_valid_number(phone_nbr_obj):
        formatted_number = phonenumbers.format_number(
            phone_nbr_obj,
            PhoneNumberFormat.NATIONAL
        )
        significant_number = ''.join(filter(str.isdigit, formatted_number))
        return significant_number

    # Fallback to the original number if parsing is not successful
    return cleaned_number or number or False
