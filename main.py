import re
import sys
from io import StringIO
import pandas as pd

REGEX_HIGHLIGHT_MARKER = r"Yellow highlight \| Page: [0-9]+,?[0-9]+|Yellow highlight \| Location: [0-9]+,?[0-9]+"
REGEX_NEWLINES = r"\n+"
REGEX_TRAILING_WHITESPACES = r"\s{2,}"
REGEX_NOTE_MARKER = r"\n+Note:"
REGEX_CHAPTER_START = r"([A-Za-z ]+-Chapter [0-9]+)"

SUB_HIGHLIGHT_MARKER = r""
SUB_NEWLINES = r""
SUB_TRAILING_WHITESPACES = r"\n\n"
SUB_NOTE_MARKER = r"-"
SUB_CHAPTER_START = r"## \1\n"


def read_textfile(filename, encoding="utf-8"):
    with open(filename, "r", encoding=encoding) as file:
        return file.read()


def get_output_filename(input_filename):
    input_filename = input_filename.split("/")[1]
    return input_filename.replace("txt", "md").replace("csv", "md")


def write_output_markdown(filename, text, encoding="utf-8"):
    with open("output/" + filename, "w", encoding=encoding) as file:
        file.write(text)
    return None


def replace_matched_passages(input_text, regex_capture, sub_text):
    return re.sub(regex_capture, sub_text, input_text)


def remove_problematic_whitespaces(input_text):
    return re.sub(r"\n{2}", r" ", input_text)


def load_csv_to_dataframe(input_text):
    return pd.read_csv(StringIO(input_text))


def extract_text_from_df(input_df):
    text_list = []
    for index, row in input_df.iterrows():
        chapter_heading = "## " + row["chapter"]
        if not chapter_heading in text_list:
            text_list.append(chapter_heading)
        text_list.append(row["quote"])
    text_output = "\n\n".join(text_list)
    return text_output


def main(argv):
    # parse command line arguments
    input_file = argv[1]
    input_type = input_file.split(".")[-1]

    # read text data
    text_data = read_textfile(input_file)

    if input_type == "txt":
        # replace passages accordingly
        text_data = replace_matched_passages(text_data, REGEX_HIGHLIGHT_MARKER, SUB_HIGHLIGHT_MARKER)
        text_data = replace_matched_passages(text_data, REGEX_NEWLINES, SUB_NEWLINES)
        text_data = replace_matched_passages(text_data, REGEX_TRAILING_WHITESPACES, SUB_TRAILING_WHITESPACES)
        text_data = replace_matched_passages(text_data, REGEX_NOTE_MARKER, SUB_NOTE_MARKER)
        text_data = replace_matched_passages(text_data, REGEX_CHAPTER_START, SUB_CHAPTER_START)
    elif input_type == "csv":
        text_data = remove_problematic_whitespaces(text_data)
        text_df = load_csv_to_dataframe(text_data)

        # reverse dataframe since entries are ordered from most to least recent
        text_df = text_df.iloc[::-1]

        text_data = extract_text_from_df(text_df)

    # set output filename
    output_file = get_output_filename(input_file)

    write_output_markdown(output_file, text_data)


if __name__ == "__main__":
    main(sys.argv)

