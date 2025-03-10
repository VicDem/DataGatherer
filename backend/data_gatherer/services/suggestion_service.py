import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from annoy import AnnoyIndex
from sklearn.feature_extraction.text import TfidfVectorizer
import sys


def get_suggestion(raw_text) -> str:
    return "disabled from code"
    try:
        with open('annoy_config.json', 'r') as f:
            config = json.load(f)
    except:
        return "username index not created"

    vector_size = config['vector_size']
    usernames = config['usernames']
    index = AnnoyIndex(vector_size, 'angular')  # Same dimension and metric used for index

    try:
        index.load('usernames_index.ann')  # Load the index from the saved file
    except:
        return "username index not created"

    if len(usernames) < 3:
        return "not available (less than 3 users exist)"

    vectorizer = TfidfVectorizer()  # Fit on new string and existing usernames
    vectorizer.fit(usernames)
    vector = vectorizer.transform([raw_text] + usernames).toarray()[0]  # Transform raw string into a vector

    # Find the nearest neighbor (the best match)
    nearest_neighbor = index.get_nns_by_vector(vector, 1)[0]  # Get the closest match (index of best match)

    return usernames[nearest_neighbor]
