import random, json
from ai_functions import query_llm
import pymongo

def process_sample_prompt_text(prompt_text=""):
    sample_responses = [
        {
            "type": "error",
            "text": "This is a sample Error in processing"
        },
        {
            "type": "success",
            "text": "Sample Processed: "+prompt_text
        },
        {
            "type": "listofitems",
            "items": [
                {
                    "item": "yellow bananas",
                    "price": 2.5                    
                },
                {
                    "item": "red apples",
                    "price": 3.5
                },
                {
                    "item": "green grapes",
                    "price": 4.5
                },
                {
                    "item": "green bananas",
                    "price": 1.5
                }
            ]
        }
    ]
    random_response= random.choice(sample_responses)
    # process the prompt text
    return random_response  

def process_real_prompt_text(prompt_text="", model="", account_id="", api_token=""):

    # Call the AI model to process the prompt text
    processed_response = query_llm(prompt_text, model, account_id, api_token)

    # print("Processed Response from Query LLM: ", str(processed_response))

    if  "prompt_process_error" in processed_response :
        return {"type":"error", "text":processed_response["prompt_process_error"]}
    if "prompt_additional_question" in  processed_response:
        return {"type":"success", "text":processed_response['prompt_additional_question']}
    if  "Description" in processed_response:
        try:
            print("searching items")
            print(processed_response)
            search_items_response = search_items(processed_response["Description"]+" "+processed_response["Department"]+" "+str(processed_response["Price"]))
            return {"type":"listofitems", "items":search_items_response}
        except Exception as e:
            print(str(e))
            return {"type":"error", "text":"Error processing prompt "+str(e)}


def get_vector_embeddings(query):
    import openai
    openai.api_key = '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'

    response = openai.embeddings.create(
    model="text-embedding-ada-002",
    input=query,
    encoding_format="float"
    )
    print("Done with embeddings")
    return response.data[0].embedding


def search_items(query_to_search):

    query_embedding = get_vector_embeddings(query_to_search)
    MONGO_URI = "mongodb+srv://ruhack:ruhack%40123@ruhack.4ow47bh.mongodb.net"
    # print(query_embedding)
    client = pymongo.MongoClient(MONGO_URI)
    # define pipeline
    pipeline = [
    {
        '$vectorSearch': {
        'index': 'vector_index', 
        'path': 'item_embedding', 
        'queryVector': query_embedding,
        'numCandidates': 1536, 
        'limit': 6
        }
        },        
        {
        '$project': {
        '_id': 0, 
        'Description': 1, 
        'Department': 1, 
        'Price': 1,
        'score': {
            '$meta': 'vectorSearchScore'
        }
        }    
        },
        # {
        #     "$match": {"score": {"$gte": 0.9}}
        # },
    ]
    # run pipeline
    result = client["RuHack"]["storeitems"].aggregate(pipeline)
    if result:
        return list(result)
        print(f'Items found: {list(result)}')
    else:
        return []
    
def service_for_getting_items():
    MMONGO_URI = "mongodb+srv://ruhack:ruhack%40123@ruhack.4ow47bh.mongodb.net"
    client = pymongo.MongoClient(MONGO_URI)
    db = client["RuHack"]
    collection = db["storeitems"]
    #get items already in the database and dont obtain the item_embedding of the items
    items = collection.find({}, {"item_embedding": 0})
    if items:
        return list(items)
    else:
        return []
    