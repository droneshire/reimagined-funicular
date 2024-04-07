import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download("stopwords")
nltk.download("punkt")


def clean_text(text):
    """
    Function to remove stop words, punctuation, and double quotes
    """
    text = text.lower()
    text = text.replace('"', "")
    # Tokenize the text into words
    words = word_tokenize(text)
    # Remove punctuation
    words = [word for word in words if word.isalnum()]
    stop_words = set(stopwords.words("english"))
    filtered_words = [word for word in words if word not in stop_words]
    cleaned_text = " ".join(filtered_words)
    return cleaned_text
