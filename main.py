from flask import Flask
from flask_cors import CORS
from flask import request
from helper_functions import process_sample_prompt_text, process_real_prompt_text, service_for_getting_items
# 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
app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "Hello from HACK RU 2024 Backend",200

@app.route("/api/inboundmessage", methods=['POST'])
def inbound_message():
    try:
        
        # model = "@cf/meta/llama-2-7b-chat-int8"
        model="@hf/thebloke/llama-2-13b-chat-awq"
        ## CloudFlare API Token and Account ID
        api_token="_pf55d9ZOQBox0sqphtb5LPe1didvRe1fEtZTdTN"
        account_id="6b5ad02398b5bc0e672a5f568195e185"
        prompt_text = request.json['prompt']
        print(prompt_text)
        # response_text = process_sample_prompt_text(prompt_text)
        response_text = process_real_prompt_text(prompt_text, model, account_id, api_token)
        return response_text, 200
    except Exception as e:
        print(str(e))
        return "Error processing prompt "+str(e),400

@app.route("/api/getitemlist", methods=['GET'])
def get_item_list():
    try:
        response = service_for_getting_items()
        return response,200
    except Exception as e:
        print(str(e))
        return "Error processing prompt "+str(e),400


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)


'''
CLOUDFLARE_API_TOKEN = _pf55d9ZOQBox0sqphtb5LPe1didvRe1fEtZTdTN

curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
     -H "Authorization: Bearer _pf55d9ZOQBox0sqphtb5LPe1didvRe1fEtZTdTN" \
     -H "Content-Type:application/json"

'''