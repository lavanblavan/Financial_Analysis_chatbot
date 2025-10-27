import os,ast,re
import sys
from bs4 import BeautifulSoup as BS
import requests as req
from groq import Groq
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from tavily import TavilyClient

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:    
    sys.path.append(root_dir)
from Configure.configure_Agent import Groq_api, tavily_api

class DataFetcher:
    def __init__(self, api_key):
        #initiate with API key
        self.api_key = api_key
        self.content_output = {}
    
    def fetch_data(self,response):
        for i, result in enumerate(response['results'], 1):
            # print(f"{i}. {result['title']}")
            # print(f"   URL: {result['url']}")
            # print(f"   Snippet: {result['content'][:200]}...\n")
            self.content_output[f"result_{i}"] = {
                "title": result['title'],
                "url": result['url'],
                "snippet": result['content']
            }
        return self.content_output


        
    
    def online_fetch(self, query):
        if isinstance(query, list):
            merged_query = "\n".join(query)
        else:
            merged_query = query
        client = TavilyClient(api_key=tavily_api)
        response = client.search(merged_query, max_results=25, search_depth="advanced")
        if response['results']:
            return response
        return "No content found."
    
    def download_page(self, response):
        full_data = {}

        for i, result in enumerate(response['results'], 1):
            url = result['url'] 
            name= result['title']

            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                }
                response = req.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BS(response.text, 'html.parser')
                paragraphs = soup.find_all('p')
                page_text = "\n".join([para.get_text() for para in paragraphs])
                full_data[f"page_{i}_{name}"] = {
                    "url": url,
                    "content": page_text
                }
        
            
            except Exception as e:
                return f"Error downloading page: {e}"
        print(full_data)
        return full_data
    
    def run_search(self, query):

        response = self.online_fetch(query)
        if response != "No content found.":
            full_pages = self.download_page(response)
            print(full_pages)  # print here, outside the download_page function
            return full_pages
        return response
    
    
