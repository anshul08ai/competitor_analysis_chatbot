import os
from dotenv import load_dotenv
from langchain_litellm import ChatLiteLLM
from pathlib import Path
import yaml



HUGGINGFACE_CONFIG_PATH = Path(__file__).parent.parent.parent  / 'config' / 'hugging_config.yaml'
def load_hugging_config():
    with HUGGINGFACE_CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)

AZURE_CONFIG_PATH = Path(__file__).parent.parent.parent  / 'config' / 'azure_config.yaml'
def load_azure_config():
    with AZURE_CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)
azure_config = load_azure_config()

PROVIDE=azure_config["PROVIDE"]
DEPLOYMENT_NAME=azure_config["DEPLOYMENT_NAME"]

load_dotenv()
 
 
def create_chat_model(provider: str=PROVIDE, model_name: str=DEPLOYMENT_NAME, temperature: float = 0.7):
    try:
        """
        Creates and returns a ChatLiteLLM instance.
        Supported providers: 'huggingface', 'azure', 'openai'
        """
        if provider=='azure':
            import litellm
            litellm.drop_params=True
            os.environ["AZURE_API_KEY"] = azure_config["AZURE_OPENAI_KEY"]
            os.environ["AZURE_API_BASE"] = azure_config["AZURE_OPENAI_ENDPOINT"]
            os.environ["AZURE_API_VERSION"] =azure_config["AZURE_TEXT_OPENAI_VERSION"]

        elif provider=='huggingface':
            hugging_config = load_hugging_config()
            os.environ["HUGGINGFACE_API_KEY"]=hugging_config['HUGGIN_FACE']
            os.environ["HUGGIN_FACE_REPO_ID"]=hugging_config['HUGGIN_FACE_REPO_ID']
        else:
            return 
        # Initialize ChatLiteLLM
        chat_model = ChatLiteLLM(
            model=f"{provider}/{model_name}",
            temperature=temperature
        )
        return {"status":True,"model":chat_model}
    except Exception as e:
        return {"status":False,"model":''}