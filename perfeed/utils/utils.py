import tiktoken
import re


def json_output_curator(llm_output):
    regex = re.compile(r'(```|json|\n)')
    return regex.sub('', llm_output)


def count_tokens(text, model="gpt-4o"):
    # Load the appropriate encoding for the model
    encoding = tiktoken.encoding_for_model(model)
    # Encode the text to get tokens
    tokens = encoding.encode(text)
    # Return the number of tokens
    return len(tokens)