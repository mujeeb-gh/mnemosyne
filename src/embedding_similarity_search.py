import chromadb
from face_index import get_face_embedding

chroma_client= chromadb.PersistentClient(path='vector_db')
collection = collection = chroma_client.get_collection(name="Face_collection")

img_path = 'src/assets/spoofed.png'
face_embedding= get_face_embedding(img_path= img_path, model_name='VGG-Face')

nearest =collection.query(
    query_embeddings=[face_embedding],
    n_results=1,
)

print("Nearest match:", nearest)