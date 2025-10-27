import os,ast,re
import sys
from groq import Groq
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from tavily import TavilyClient

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:    
    sys.path.append(root_dir)
from Configure.configure_Agent import Groq_api, tavily_api

class SummaryCreator:
    def __init__(self, api_key):
        #initiate with API key
        self.api_key = api_key
    
    def generate_summary(self, data):
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
        message_llm = chain.invoke({"input": data})
        summary = message_llm.content
        return summary
    def prompt_Summarizer(self):
         return """You are a financial content summarization agent. Your task is to read through the provided financial documents and generate concise summaries that capture the key points, trends, and insights relevant to financial analysis. Ensure that the summaries are clear, informative, and useful for decision-making in a financial context. and make it as an executive summary."""