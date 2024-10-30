import cv2
from deepface import DeepFace
from typing import List, Literal
from pymilvus import MilvusClient

# Set up Milvus client
# milvus_client = MilvusClient(host='localhost', port='19530', db_name='mnemosyne_face_db.db')


# Get face embedding
def get_face_embedding(img_path, model_name: Literal['VGG-Face', 'Facenet', 'OpenFace', 'DeepFace', 'DeepID', 'ArcFace', 'Dlib']) -> List[float]:
  face_embedding = DeepFace.represent(img_path, model_name=model_name, enforce_detection=True)
  embedding_vector = face_embedding[0]['embedding']
  embedding_dimension = len(embedding_vector)
  print(f"Embedding dimension: {embedding_dimension}")
  return embedding_vector

img_path = 'assets\centralized_face.png'

# print(face_embedding)

if __name__ == "__main__":
    get_face_embedding(img_path, model_name='VGG-Face')