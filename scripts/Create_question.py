import os,ast,re
import sys
from groq import Groq
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)
from Configure.configure_Agent import Groq_api

class DataFetcher:
    def __init__(self, api_key):
        #initiate with API key
        self.api_key = api_key
    
    def search_enhancer(self, query):
        # Create multiple relevant questions based on the user query
        print(f"Fetching data for query: {query} using API key: {self.api_key}")
        chat_prompt = self.prompt()
        client = Groq(api_key=self.api_key)
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
            self.prompt(),
        ),
        ("human", "{input}"),
    ]
)
        chain = prompt | llm
        message_llm = chain.invoke({"input": query})

        
        
        # print("Response from local LLM:", message_llm.content)
        llm_questions =self.store_questions(message_llm.content)
        # print("Extracted Questions:", llm_questions)

        response =  client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": self.prompt(),
            },
            {
                "role": "user",
                "content": query,
            }
        ],
    model="llama-3.1-8b-instant",
)
        # print("Response from Groq API:", response.choices[0].message.content)
        llm_questions =self.store_questions(response.choices[0].message.content)
        # print("Questions from Groq API:", response.choices[0].message.content)
        print("Extracted Questions from groq:", llm_questions)
    
    def prompt(self):
        prompt = r"""You are a financial data retrieval agent
        Your task is to fetch the relevant data from the web but not exactly not the question first need to understand the question if you understand the question you need to ask more relevant questions for the user to get more clarity on the question once you have clarity you need to fetch the data from the web using the search_enhancer function and provide the data to the user.
        When you give the question make it as user ask the web search question for example "what is the latest news about Apple Inc.?" you need to ask like what is latest products of apple like that
Like what's new with the company then you need to check what is the new products of x company and how they do financially does now you need to consider all the relevant question ask about then create new questionnaire and get the answer for that also like wise create important related 5 questions and store it in a dictionary {{"question1":"", "question2":"", "question3":"", "question4":"", "question5":""}} in your output only give the 5 questions in dictionary don't give any explanations"""
        return prompt
    
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
    fetcher = DataFetcher(Groq_api)
    fetcher.search_enhancer("Latest financial news about Apple Inc.")