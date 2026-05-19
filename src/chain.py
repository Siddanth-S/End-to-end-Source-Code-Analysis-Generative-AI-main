from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain


def create_qa_chain(llm, vectordb):
    """Create Q&A chain with memory and retriever"""
    
    memory = ConversationBufferMemory(
        memory_key="chat_history", 
        return_messages=True
    )
    
    retriever = vectordb.as_retriever(
        search_type="mmr", 
        search_kwargs={"k": 8}
    )
    
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm,
        retriever=retriever,
        memory=memory
    )
    
    return qa_chain