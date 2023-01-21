import os
import requests
import cyrtranslit

HEADER_AUTH_TEMPLATE = 'Authorization: DeepL-Auth-Key {}'

MISSING_DEEPL_API_KEY = """Please register yourself as a developer at
deepl.com and add api key to environment variable DEEPL_API_KEY. See readme
for more information"""

def translit(input_text,source_language = "ru"):
    return cyrtranslit.to_latin(input_text, "ru")

def translate(input_text, target_language = "EN-US",api_key=None, uri=None): 

    if api_key is None:
        api_key = os.getenv("DEEPL_API_KEY")
        assert api_key is not None, MISSING_DEEPL_API_KEY

    if uri is None:
        uri = os.getenv("DEEPL_URI")
        assert uri is not None, "Set DEEPL_URI env var"
    headers = {
        "Authorization": f"DeepL-Auth-Key {api_key}"
    }

    data = {
        "text": input_text,
        "target_lang": target_language,
        "source_lang": "RU",
        "tag_hangling": "xml"
    }
    
    response = requests.post(uri, headers=headers,data=data)
    if response.status_code < 200 or response.status_code >=400:
        raise Exception(f"Couldn't translate due to an error: {response.text}")
    response_json = response.json()
    texts = [ translation['text'] for translation in response_json['translations']]
    return ' '.join(texts)

