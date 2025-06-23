# File: agent.py
from typing import List, Dict, TypedDict, Optional

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import Document
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.retrievers.multi_query import MultiQueryRetriever
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END

from config import PINECONE_INDEX_NAME

# --- AGENT STATE AND PYDANTIC MODELS ---
class AgentState(TypedDict):
    question: str
    chat_history: List[BaseMessage]
    context: List[Document]
    answer: str
    evaluation: Optional[Dict]
    iteration: int

class Evaluation(BaseModel):
    is_supported: bool = Field(description="True if the answer is fully supported by the context, False otherwise.")
    reasoning: str = Field(description="A brief explanation of why the answer is or is not supported.")

# --- THE MAIN AGENT CLASS ---
class AgenticAssistant:
    def __init__(self, google_api_key: str):
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=google_api_key)
        self.generator_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3, google_api_key=google_api_key)
        self.evaluator_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=google_api_key)
        base_retriever = PineconeVectorStore.from_existing_index(index_name=PINECONE_INDEX_NAME, namespace="code-chunks", embedding=self.embeddings).as_retriever(search_kwargs={"k": 5})
        self.code_retriever = MultiQueryRetriever.from_llm(retriever=base_retriever, llm=self.generator_llm)
        self.app = self._build_graph()

    def _retrieve_node(self, state: AgentState) -> AgentState:
        print("--- 🔄 NODE: RETRIEVE CODE ---")
        question = state["question"]
        relevant_docs = self.code_retriever.invoke(question)
        for doc in relevant_docs:
            doc.page_content = f"// FILE: {doc.metadata['file_path']}\n\n{doc.page_content}"
        return {"context": relevant_docs, "iteration": state.get("iteration", 0) + 1}

    def _generate_node(self, state: AgentState) -> AgentState:
        print("--- 🔄 NODE: GENERATE ---")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert AI programming assistant. Answer the user's current question based on the provided code context and the conversation history. If the user asks about the conversation itself, answer from the history."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "CONTEXT FROM CODEBASE (if any):\n{context}\n\nUSER'S CURRENT QUESTION: {question}")
        ])
        context_str = "\n\n---\n\n".join([doc.page_content for doc in state["context"]])
        chain = prompt | self.generator_llm
        # Pass the full state, so the chain can access 'context', 'question', and 'chat_history'
        answer = chain.invoke(state).content
        return {"answer": answer}

    def _evaluate_node(self, state: AgentState) -> AgentState:
        print("--- 🔄 NODE: EVALUATE ---")
        prompt_str = f"Based ONLY on the following source code snippets, determine if the AI's answer is factually supported. Ignore conversation history for this check.\n\nSOURCE CODE CONTEXT:\n{[doc.page_content for doc in state['context']]}\n\nAI'S ANSWER:\n{state['answer']}"
        evaluator_chain = self.evaluator_llm.with_structured_output(Evaluation)
        evaluation_result = evaluator_chain.invoke(prompt_str)
        print(f"  > Evaluation: {evaluation_result.is_supported}. Reason: {evaluation_result.reasoning}")
        return {"evaluation": evaluation_result.dict()}

    # --- THIS IS THE FULLY IMPLEMENTED METHOD ---
    def _should_continue(self, state: AgentState) -> str:
        print("--- ❔ CONDITIONAL EDGE ---")
        if state["iteration"] > 2:
            print("  > Max iterations reached. Finishing.")
            return "end"
        # If the evaluator approved the answer, end the loop.
        if state["evaluation"] and state["evaluation"]["is_supported"]:
            return "end"
        # Otherwise, continue the loop to try again.
        else:
            return "continue"
    
    # --- THIS IS THE FULLY IMPLEMENTED METHOD ---
    def _build_graph(self):
        """Assembles the complete LangGraph agent with all connections."""
        workflow = StateGraph(AgentState)
        
        # Add all the nodes
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("generate", self._generate_node)
        workflow.add_node("evaluate", self._evaluate_node)
        
        # Set the entry point, telling the graph where to start
        workflow.set_entry_point("retrieve")
        
        # Add the standard edges
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", "evaluate")
        
        # Add the conditional edge for the self-correction loop
        workflow.add_conditional_edges(
            "evaluate",
            self._should_continue,
            {
                "end": END,
                "continue": "retrieve",
            }
        )
        
        return workflow.compile()

    async def query_stream(self, question: str, chat_history: List[dict]):
        langchain_history = []
        for msg in chat_history:
            if msg['role'] == 'user':
                langchain_history.append(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                langchain_history.append(AIMessage(content=msg['content']))

        inputs = {"question": question, "chat_history": langchain_history}
        final_state = {}
        try:
            async for event in self.app.astream_events(inputs, version="v1"):
                kind = event["event"]
                if kind == "on_chain_start" and event["name"] != "LangGraph":
                    yield {"type": "status_update", "data": {"node": event["name"]}}
                elif kind == "on_chain_end" and event["name"] != "LangGraph":
                    if isinstance(event["data"]["output"], dict):
                        final_state.update(event["data"]["output"])
            
            final_state.pop("context", None)
            yield {"type": "final_answer", "data": final_state}
        except Exception as e:
            print(f"❌ Error during agent query stream: {e}")
            yield {"type": "error", "data": {"message": str(e)}}