from string import punctuation


def clean_text(text: str) -> str:
    """
    Function to remove stop words, punctuation, and double quotes
    """
    text = text.lower()
    text = text.replace('"', "")
    text = text.replace("“", "").replace("”", "")
    text = text.replace("\n", " ")
    text = text.translate(str.maketrans("", "", punctuation))
    return text
