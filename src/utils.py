import os
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(
    api_key=os.environ.get("PINECONE_API_KEY")
)

# Now do stuff
if 'my_index' not in pc.list_indexes().names():
    pc.create_index(
        name='my_index', 
        dimension=1536, 
        metric='euclidean',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-west-2'
        )
    )
