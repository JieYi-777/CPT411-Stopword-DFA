import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re


# The class of stopword DFA, it contains DFA for all stopword
class StopwordDFA:
    def __init__(self, stopwords):
        # Define transitions
        self.transitions = {}
        # Define accepting states
        self.accepting_states = set()
        self.stopwords = set(stopwords)
        self.build_dfa()

    def build_dfa(self):
        # Define transitions and accepting states based on stopwords
        for word in self.stopwords:
            current_state = 0
            for char in word:
                if (current_state, char) not in self.transitions:
                    # Transition to a new state
                    self.transitions[(current_state, char)] = len(self.transitions) + 1
                current_state = self.transitions[(current_state, char)]
            # Mark the final state as accepting
            self.accepting_states.add(current_state)

    def is_stopword(self, word):
        current_state = 0
        for char in word:
            if (current_state, char) in self.transitions:
                current_state = self.transitions[(current_state, char)]
            else:
                return False
        return current_state in self.accepting_states


# To get the stopwords from nltk and can add additional stopword for customization
def get_stopwords():
    # Download NLTK stopwords list
    nltk.download('stopwords')

    # Get the stopword list
    stopwords_list = stopwords.words('english')

    # List of additional stopwords to append
    additional_stopwords = ["can't"]

    # Add additional stopwords to the stopwords list
    stopwords_list.extend(additional_stopwords)

    # Sort it
    stopwords_list.sort()

    return stopwords_list


# To convert the text into tokens
def tokenize(text):
    # Define patterns to capture contractions like "didn't", "shouldn't", etc.
    contraction_patterns = r"\b(?:aren't|can't|couldn't|didn't|doesn't|don't|hadn't|hasn't|haven't|isn't|mightn't|mustn't|needn't|shan't|shouldn't|wasn't|weren't|won't|wouldn't)\b"

    # Replace contractions with unique placeholders
    # (To avoid separating issue when tokenizing, for issue example: aren't will separate to "are" and "n't")
    text = re.sub(contraction_patterns, lambda match: match.group(0).replace("'", "|||"), text)

    # Tokenize the text using NLTK's word_tokenize function
    tokens = word_tokenize(text)

    # Replace placeholders back to contractions
    tokens = [token.replace("|||", "'") for token in tokens]

    return tokens


# To preprocess the text
def preprocess_words(text):
    # To lower the text (because the stopwords are lowercase)
    text = text.lower()

    # Get the tokens
    tokens = tokenize(text)

    # To store the valid tokens
    processed_tokens = []

    # Remove symbols from tokens
    for token in tokens:
        # Remove non-alphanumeric characters if token has only one character
        if len(token) == 1 and not token.isalnum():
            continue
        processed_tokens.append(token)

    return processed_tokens


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Download NLTK stopwords list
nltk.download('stopwords')

# Example usage
stopwords_list = stopwords.words('english')
dfa = StopwordDFA(stopwords_list)

# Test words
test_strings = [
    "the",  # Should be identified as stopword
    "quick",  # Should not be identified as stopword
    "brown",  # Should not be identified as stopword
    "fox",  # Should not be identified as stopword
    "jumps",  # Should not be identified as stopword
    "over",  # Should not be identified as stopword
    "lazy",  # Should not be identified as stopword
    "dog"  # Should not be identified as stopword
]

for word in test_strings:
    if dfa.is_stopword(word):
        print(f"'{word}' is a stopword.")
    else:
        print(f"'{word}' is not a stopword.")
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
