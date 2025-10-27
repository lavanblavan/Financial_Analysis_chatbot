import os,ast,re
import sys
from groq import Groq
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)
from Configure.configure_Agent import Groq_api

class question_generator:
    def __init__(self, api_key):
        #initiate with API key
        self.api_key = api_key
    
    def search_enhancer(self, query):
        # Create multiple relevant questions based on the user query
        
        
        llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=None,
    
    timeout=None,
    max_retries=2,
    groq_api_key=self.api_key
    # other params...
)
        prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            self.prompt_langchain(),
        ),
        ("human", "{input}"),
    ]
)
        chain = prompt | llm
        message_llm = chain.invoke({"input": query})

        
        
        
        llm_questions =self.store_questions(message_llm.content)
        
        return llm_questions

         
    
    def prompt_langchain(self):
         return """You are a financial related question generation agent.
         Your task is to generate 5 relevant questions based on the user query to get more clarity on the question what I hope from you is your output should be in the dictionary data type by reading the dictionary we should be able to find if I need to get more clarify in the financial status of the company or the products or the market trends so your output should be like {{"question1":"", "question2":"", "question3":"", "question4":"", "question5":""}} only give the questions in the dictionary don't give any explanations
         But when creating questions avoid asking about the answers which could be related to stocks mainl focus on financial analysis, market trends, investment strategies, economic indicators, and company performance.
         Your task """
    
    import re, ast

    def store_questions(self, llm_response, first_only=True):
        """
        Extract dictionary(ies) from LLM response text.
        If first_only=True, returns the first dict found.
        If first_only=False, returns a list of all dicts.
        """
        extracted_dicts = []

        # Find all {…} blocks
        matches = re.findall(r"\{.*?\}", llm_response, re.DOTALL)
        for dict_text in matches:
            try:
                d = ast.literal_eval(dict_text)
                extracted_dicts.append(d)
            except Exception as e:
                print("⚠️ Could not parse dictionary:", e)

        if not extracted_dicts:
            fallback = {
                "question1": "",
                "question2": "",
                "question3": "",
                "question4": "",
                "question5": "",
            }
            return fallback if first_only else [fallback]

        return extracted_dicts[0] if first_only else extracted_dicts


if __name__ == "__main__":
    generator = question_generator(Groq_api)
    generator.search_enhancer("Latest financial news about Apple Inc.")