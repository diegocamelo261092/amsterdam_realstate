# External Packages
import re

"""
Description to be added here...
"""


# -------- FUNCTIONS DEFINITION -----------

def text_to_float(string):
    """
    Description to be added...
    :param: string field description...
    """

    try:
        return_data = float(re.sub('[^0-9,]', '', str(string)))
    except:
        return_data = string
    return return_data


def text_to_int(string):
    return int(re.sub('[^0-9,]', '', str(string)))


def text_clean_up(text):
    text = re.sub(r'[^A-Za-z0-9,. ]+', '', text)
    return str(text).strip()


def returns_int_only(list):
    return [float(x) for x in list if x.isdigit()]


def string_to_int_list(str_ints):
    return re.findall('[0-9]+', str_ints)