import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HANDWRITINGOCR_API_KEY = os.getenv("HANDWRITINGOCR_API_KEY")
