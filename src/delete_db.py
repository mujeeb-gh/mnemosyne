import chromadb
import uuid
from datetime import datetime

# Initialize Chroma client and collection
chroma_client= chromadb.PersistentClient(path='vector_db')
collection = chroma_client.get_collection(name="Face_collection")


matric_no = input('matric number?') 


collection.delete(

    ids=[matric_no]
)
# Verify the latest entry
print("Last entry metadata:", collection.get(ids=[matric_no]))
View=collection.get()
print(View)