import numpy as np
from sklearn.cluster import KMeans
from collections import defaultdict

def encode_genre_vector(genres, all_genres):
    genre_vector = [1 if genre in genres else 0 for genre in all_genres]
    return genre_vector

def cluster_books(results, num_clusters):
    all_genres = sorted({genre for book in results for genre in book['Genres']})
    genre_vectors = [encode_genre_vector(book['Genres'], all_genres) for book in results]

    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    clusters = kmeans.fit_predict(genre_vectors)
    
    return clusters

def group_books_by_clusters(results, clusters):
    grouped_books = defaultdict(list)
    for book, cluster in zip(results, clusters):
        grouped_books[cluster].append(book)
    return grouped_books
