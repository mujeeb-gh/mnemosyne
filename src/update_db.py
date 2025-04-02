import chromadb
from datetime import datetime

# Initialize Chroma client and collection
chroma_client= chromadb.PersistentClient(path='vector_db')
collection = chroma_client.get_collection(name="Face_collection")

matric_no = '20/sci01/031'
metadata = {
    "name": "Amrasa Tejiri",
    "email": "amrasaTejiri@gmail.com",
    "program": "Computer Science",
    "year_of_study": 5,
    "date_of_birth": "2002-10-20",
    "phone_number": "+3289327890",
    "timestamp": datetime.now().isoformat() 
}
collection.update(
    metadatas=[metadata],
    ids=[matric_no]
)
# Verify the latest entry
print("Last entry metadata:", collection.get(ids=[matric_no]))