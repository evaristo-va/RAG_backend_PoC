import cohere
import os
from dotenv import load_dotenv

# Load environment variables (.env file)
load_dotenv()

# Get the API key 
cohere_api_key = os.getenv("COHERE_API_KEY")
client = cohere.Client(api_key=cohere_api_key)

# function to generate vector embeddings of a chunk
# note input type should be search_document or search_query
def vector_embedder(text:str, input_type: str = 'search_document') -> list[float]:
    response = client.embed(texts=[text], model="embed-english-v3.0", input_type=input_type)
    return response.embeddings[0]
