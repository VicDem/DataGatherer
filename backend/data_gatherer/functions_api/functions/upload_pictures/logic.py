import hashlib
import PIL
from PIL import Image
import numpy as np
from django.contrib.auth.models import User


def average_hash(image_path, hash_size=25):
    # Apri l'immagine e convertila in scala di grigi
    img = Image.open(image_path).convert('L')

    # Ridimensiona l'immagine
    img = img.resize((hash_size, hash_size)).getdata()

    # Converti l'immagine in un array numpy
    pixels = np.array(img)

    # Calcola la media dei pixel
    avg = pixels.mean()

    # Genera l'hash: 1 se il pixel è superiore alla media, 0 altrimenti
    hash_array = (pixels > avg).astype(int)

    # Converte l'array di bit in una stringa di bit
    hash_str = ''.join(str(x) for x in hash_array.flatten())

    return hash_str


def distanza_di_hamming(hash1, hash2):
    # Assicurati che i due hash abbiano la stessa lunghezza
    if len(hash1) != len(hash2):
        raise ValueError("Gli hash devono avere la stessa lunghezza")

    # Calcola la distanza di Hamming
    distanza = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))

    return distanza


def _are_images_similar(image1_path, image2_path, threshold=5):
    hash1 = average_hash(image1_path)
    hash2 = average_hash(image2_path)
    distance = distanza_di_hamming(hash1, hash2)
    return distance < threshold


def _are_hashes_similar(hash1, hash2, threshold=5):
    distance = distanza_di_hamming(hash1, hash2)
    return distance < threshold


def check_similarity_between_project_images(project, images_to_check):
    from storage_api.models.image_models import Image as ModelImage
    prj_images = ModelImage.objects.filter(project=project)

    for img in images_to_check:
        for compare_to_img in prj_images.exclude(
                pk=img.pk,
        ):
            if img.average_hash is None or img.average_hash == '':
                img.average_hash = average_hash(img.file.path)
                img.save()

            if compare_to_img.average_hash is None or compare_to_img.average_hash == '':
                compare_to_img.average_hash = average_hash(compare_to_img.file.path)
                compare_to_img.save()

            if _are_hashes_similar(
                img.average_hash,
                compare_to_img.average_hash,
                2
            ):
                print('Images %s and %s are similar! ' % (compare_to_img.userId, img.userId))

                if compare_to_img.isSimilarTo == img:
                    continue

                if compare_to_img.isSimilarTo is not None:
                    img.isSimilarTo = compare_to_img.isSimilarTo
                    img.save()
                    continue

                img.isSimilarTo = compare_to_img
                img.save()
                continue


def upload_files(files, project, user:User):
    from storage_api.models.image_models import Image as ModelImage
    images_to_check = []
    for file in files:
        entity: Image = ModelImage.objects.filter(project=project).order_by('userId').last()
        value = 1
        if entity is not None:
            value = entity.userId + 1
        image = ModelImage(
            file=file,
            userId=value,
            project=project,
            author=user
        )
        image.save()
        images_to_check.append(image)
    #check_similarity_between_project_images(project, images_to_check)
