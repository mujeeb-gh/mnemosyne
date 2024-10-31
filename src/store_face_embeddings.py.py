import chromadb
from face_index import get_face_embedding
import uuid
from datetime import datetime

# Initialize Chroma client and collection
chroma_client= chromadb.PersistentClient(path='vector_db')
collection = chroma_client.get_collection(name="Face_collection")

# Define the path and get the embedding for the image
img_path = 'assets/centralized_face.png'
face_embedding = get_face_embedding(img_path, model_name='VGG-Face')

# Generate a unique ID for each entry
matric_no = '20/sci01/031'  # Replace with actual matric numbers or identifiers if unique per student
# Appends a unique UUID to the matric number

# Define metadata
metadata = {
    "name": "John Doe",
    "email": "johndoe@example.com",
    "program": "Computer Science",
    "year_of_study": 2,
    "date_of_birth": "2000-01-01",
    "phone_number": "+1234567890",
    "timestamp": datetime.now().isoformat()  # Optional timestamp
}
print(face_embedding)
# Upsert the face embedding and metadata with the unique ID
collection.add(
    embeddings=[face_embedding],
    metadatas=[metadata],
    ids=[matric_no]
)
# Verify the latest entry
print("Last entry metadata:", collection.get(ids=[matric_no]))