import json

from annoy import AnnoyIndex
from sklearn.feature_extraction.text import TfidfVectorizer


def compute_index():
    num_trees = 10

    from storage_api.models.data_models import IGUser, UserHashtagUse
    usernames = list(UserHashtagUse.objects.all().values_list('igUser__name', flat=True).distinct())
    #usernames = list(IGUser.objects.all().values_list('name', flat=True))

    usernames = [s for s in usernames if "follow" not in s.lower()]

    # Convert usernames and raw_string into vectors using TF-IDF
    vectorizer = TfidfVectorizer()
    vectorizer.fit(usernames)
    vectors = vectorizer.transform(usernames).toarray()

    # Initialize Annoy index (using 10 trees)
    index = AnnoyIndex(vectors.shape[1], 'angular')  # 'angular' is for cosine similarity

    # Add username vectors to the Annoy index
    for idx, vector in enumerate(vectors):
        index.add_item(idx, vector)

    # Build the index
    index.build(num_trees)  # You can adjust the number of trees (higher = more accurate, slower)

    # Save the index to a file
    index.save('usernames_index.ann')  # Save to file 'usernames_index.ann'

    from contextlib import redirect_stdout

    # Salva la configurazione (vector_size e num_trees)
    config = {'vector_size': vectors.shape[1], 'num_trees': num_trees, 'usernames': usernames}

    # Salva la configurazione in un file JSON
    with open('annoy_config.json', 'w') as f:
        json.dump(config, f)

    print("Annoy index saved successfully!")


