import typing as T

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


def parse_itenerary_day(lines: T.List[str]) -> T.List[T.Tuple[str, str]]:
    day_plan = []
    for line in lines:
        # sometimes divided by `:` and sometimes by `at`
        try:
            activity_type, place = line.split(":")
        except ValueError:
            print(f"Could not parse line: {line}")
            continue

        try:
            activity_type, place = line.split("at")
        except ValueError:
            print(f"Could not parse line: {line}")
            continue

        # sometimes the activity type is prefixed with a number
        try:
            activity_type = activity_type.split()[1]
        except IndexError:
            print(f"Could not parse activity type: {activity_type}")

        # remove any `(*)` in the place name
        try:
            place = place.split("(")[0]
        except IndexError:
            pass

        activity_type = activity_type.strip()
        place = place.strip()
        day_plan.append((activity_type, place))

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
