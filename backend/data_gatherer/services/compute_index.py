# compute_index.py
from annoy import AnnoyIndex
from sklearn.feature_extraction.text import TfidfVectorizer


def compute_indexes(usernames):

    # Convert usernames and raw_string into vectors using TF-IDF
    vectorizer = TfidfVectorizer()
    vectorizer.fit(usernames)
    vectors = vectorizer.transform(usernames).toarray()

    # Initialize Annoy index (using 10 trees)
    index = AnnoyIndex(vectors.shape[1], 'angular')  # 'angular' is for cosine similarity

    # Add the raw string vector to the Annoy index (index 0)
    index.add_item(0, vectors[0])

    # Add username vectors to the Annoy index (index 1 onwards)
    for idx, vector in enumerate(vectors[1:], start=1):
        index.add_item(idx, vector)

    # Build the index
    index.build(10)  # You can adjust the number of trees (higher = more accurate, slower)

    # Save the index to a file
    index.save('usernames_index.ann')  # Save to file 'usernames_index.ann'

    print("Annoy index saved successfully!")
