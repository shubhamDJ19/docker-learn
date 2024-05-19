import os
import dotenv
dotenv.load_dotenv("./.env")

def getOpenAPIkey():
    return os.environ.get('OPENAI_API_KEY')

def getHFKey():
    return os.environ.get('HF_TOKEN')