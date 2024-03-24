import requests
import json


def query_llm(og_query:str, model:str, account_id:str, api_token:str):
    og_prompt = {
        "messages": [
            {
                "role": "system",
                "content": "You are a smart shopping assistant. Respond to queries with structured JSON containing 'Description', 'Department', and 'Price' fields. If information is missing or further clarification is needed, return a JSON with 'prompt_additional_question' containing your question.",
            },
            {
                "role": "user",
                "content":og_query
            },
            {
                "role": "system",
                "content": "Strictly give response in ONLY JSON format with the following grammar: {'Description': <description>, 'Department': <department>, 'Price': <price>}."

            },
            {
                "role": "system",
                "content":  "If you are unsure then try to clarify by follwing JSON grammar as {'prompt_additional_question': <your_question>} and refrain from including any text outside curly brackets {}. "
            },
            # {
            #     "role": "system",
            #     "content": "Please include either of the json and do not return anything else apart from the two JSON "
            # }
        ]
    }

    count = 0

    def extract_json_and_refine(prompt, model, account_id, api_token):
        nonlocal count
        # Initial request to the model
        response = requests.post(
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}",
            headers={"Authorization": f"Bearer {api_token}"},
            json=prompt
        )
        
        
        # Extract the model's response
        try:
            inference = response.json()
            model_response = inference["result"]["response"]
            # print(f' Model Response: {model_response}')
            
            
            # Attempt to extract JSON from the response
            try:
                # Assuming the JSON response is within the text
                extracted_json = (model_response[model_response.index("{"):model_response.rindex("}") + 1]).replace("'", '"' )
                extracted_json = json.loads(extracted_json)
                # print(f' Extracted JSON: {str(extracted_json)}')
                
                # Validate the extracted JSON (you can implement specific checks here)
                if ("Description" in extracted_json and "Department" in extracted_json and "Price" in extracted_json) or ("prompt_additional_question" in extracted_json):
                    return extracted_json
                else:
                    raise ValueError("Incomplete JSON structure")
            
            except (json.JSONDecodeError, ValueError):
                print("Invalid JSON format", json.JSONDecodeError, ValueError)
                # If JSON is invalid or incomplete, trigger feedback for clarification
                # This is a simplified version. You might need to adjust it based on how you can actually interact with the model for follow-ups.
                clarification_prompt = {
                    "messages": [
                        *og_prompt["messages"],
                        {"role": "system", "content": "The response was not in the correct format. Please provide the information in the correct JSON format as {'Description': <description>, 'Department': <department>, 'Price': <price>} or if additional ."}
                    ]
                }
                count += 1
                print(count)
                if count > 2:
                    return {"prompt_process_error": "Sorry, Unable to understand the query after thinking for a while. Please try again with a different query."}
                return extract_json_and_refine(clarification_prompt, model, account_id, api_token)
        
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {"prompt_process_error": "Sorry, Unable to understand the query after thinking for a while. Please try again with a different query."}
    
    
    final_response = extract_json_and_refine(og_prompt, model, account_id, api_token)
    return (final_response)
