import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")
XAI_API_ENDPOINT = "https://api.xai.com/v1/completions"
MODULES_PER_PAGE = 5

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)