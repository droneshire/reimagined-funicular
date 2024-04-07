import typing as T
import re

import nltk
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize

nltk.download("averaged_perceptron_tagger")
nltk.download("punkt")
nltk.download("stopwords")


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


def parse_itenerary_day(lines: T.List[str]) -> T.List[T.Tuple[str, str]]:
    day_plan = []
    # This pattern is designed to capture two groups separated by various delimiters
    pattern = re.compile(r"\s*([\w\s]+?)\s*(?::|at|-)\s*([\w\s'&]+)")

    for line in lines:
        match = pattern.match(line)
        if match:
            activity_type, place = match.groups()
            activity_type = activity_type.strip()
            place = place.split("(")[0].strip()  # Removes anything within parentheses
            day_plan.append((activity_type, place))
        else:
            print(f"Could not parse line: {line}")

    return day_plan


def parse_itenerary_content(content: str) -> T.List[T.Dict[str, str]]:
    # Split the content into days and activities
    days = content.split("\n\n")
    data = []
    for day in days:
        lines = day.split("\n")
        day_number = lines[0].split(" ")[1]
        day_plan = parse_itenerary_day(lines[1:])
        for activity_type, place in day_plan:
            data.append(
                {"Day": day_number, "Activity Type": activity_type, "Place": place}
            )

    return data
