from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os, sys

load_dotenv()
Root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if Root not in sys.path:
    sys.path.append(Root)

from Configure.configure_Agent import Groq_api,tavily_api
from scripts.Create_question import question_generator
from scripts.Search_question import DataFetcher

# ✅ 1️⃣ Define the shared state schema
class FinancialState(TypedDict, total=False):
    user_query: Optional[str]
    questions: Optional[List[str]]
    answers: Optional[List[str]]
    output: Optional[str]


# ✅ 2️⃣ Define the agent class
class FinancialAnalystAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.question_generator = question_generator(api_key)

    def start_question_generation(self, user_query: str) -> List[str]:
        print(f"Starting question generation for query: {user_query}")
        questions = self.question_generator.search_enhancer(user_query)
        return questions
    
    def get_answer(self, question: str) -> str:
        fetcher = DataFetcher(api_key=tavily_api)
        search_results = fetcher.run_search(question)
        if isinstance(search_results, dict):
            answer = "\n".join([f"{v['title']}: {v['snippet']}" for k, v in search_results.items()])
            return answer
        return "No relevant information found."

    def financial_analysis_agent(self):
        # ✅ Pass the state schema here
        graph = StateGraph(FinancialState)

        # --- Define nodes ---
        def start_node(state: FinancialState) -> FinancialState:
            print("🟢 Start node reached.")
            return {"message": "Please provide your financial query."}

        def generate_questions_node(state: FinancialState) -> FinancialState:
            user_query = state.get("user_query", "")
            # print(f"🔍 Generating questions for: {user_query}")
            questions = self.start_question_generation(user_query)
            return {"questions": questions}

        def generate_answer_node(state: FinancialState) -> FinancialState:
            questions = state.get("questions", [])
            merged_query = "\n".join(
                [f"{i+1}. {q}" for i, q in enumerate(questions)]
                )
    
            # print(f"🔎 Merged Tavily Query:\n{merged_query}\n")
            answers = []

            answer = self.get_answer(merged_query)

            return {"answers": answer}
        
        



        def end_node(state: FinancialState) -> FinancialState:
            
            answers = state.get("answers", "No answers found.")
            # print("\n✅ Final Tavily Search Summary:\n", answers[:500], "...\n")  # show snippet of content

            return {"output": f"Generated Answers:\n{answers}"}
        # --- Register nodes ---
        graph.add_node("start", start_node)
        graph.add_node("generate_questions", generate_questions_node)
        graph.add_node("generate_answer", generate_answer_node)
        graph.add_node("end", end_node)

        # --- Define edges ---
        graph.add_edge(START, "start")
        graph.add_edge("start", "generate_questions")
        graph.add_edge("generate_questions", "generate_answer")
        graph.add_edge("generate_answer", "end")
        graph.add_edge("end", END)

        # ✅ Compile the graph into a runnable object
        return graph.compile()
if __name__ == "__main__":
    agent = FinancialAnalystAgent(api_key=Groq_api)
    financial_agent = agent.financial_analysis_agent()
    initial_state: FinancialState = {"user_query": "What is the current financial state of Apple in 2025?"}
    final_state = financial_agent.invoke(initial_state)
    # print("Final Output:", final_state.get("output", ""))