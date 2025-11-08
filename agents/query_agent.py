import json

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

from config.config import MODEL_HOST, MODEL_NAME
from models.models import TMDBSearchSpec

llm = OllamaLLM(base_url=MODEL_HOST,model=MODEL_NAME,verbose=True)
prompt = PromptTemplate(
         input_variables=["query"],
         template="You are a TMDB /discover query builder.\n"
                "User describes movie preferences.\n"
                "Return ONLY JSON with keys:\n"
                "  include_genres, exclude_genres (array of strings)\n"
                "  language (2-letter or null)\n"
                "  region (2-letter or null)\n"
                "  min_year, max_year (int or null)\n"
                "  min_vote_average, max_vote_average (float or null)\n"
                "  sort_by (e.g. 'popularity.desc')\n"
                "  adult true or false \n "
                "  discover_limit (20-100)\n"
                "Defaults:\n"
                "- If region not given, use 'IN'\n"
                "- If 'recent' mentioned: min_year=2018\n"
                "- If family / light / kids : add 'horror' to exclude_genres and set adult to false\n"
                "- Always use most spoken language from given region unless language is explicitly defined"  
                "- Use genres that TMDB supports (e.g. 'comedy','romance','science fiction')\n"
                "Output valid JSON only.\n\n"
                "User: {query} and region {region}"
    )

chain = prompt | llm

def build_search_spec(query:str,region:str="IN") -> TMDBSearchSpec:
    llm_response = chain.invoke({"query":query,"region":region})
    try:
        model_req = json.loads(llm_response)
    except json.JSONDecodeError:
        model_req = {
            "include_genres": [],
            "exclude_genres": [],
            "language": None,
            "region": region,
            "min_year": None,
            "max_year": None,
            "min_vote_average": None,
            "max_vote_average": None,
            "sort_by": "popularity.desc",
            "discover_limit": 50,
        }
    print(f"Search Spec from LLM {model_req}")
    return TMDBSearchSpec(**model_req)

