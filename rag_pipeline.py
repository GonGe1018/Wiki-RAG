import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI


class RAGPipeline:
    def __init__(self, index_dir="faiss_index", openai_api_key=None):
        """
        Initializes the RAGPipeline.
        
        Args:
            index_dir (str): Directory to store or load the FAISS index.
            openai_api_key (str): OpenAI API key for embedding and LLM.
        """
        self.index_dir = index_dir
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=openai_api_key)
        self.openai_api_key = openai_api_key

    def prepare_data(self, res_list):
        """
        Prepares FAISS index from crawled data.
        
        Args:
            res_list (list): List of tuples (title, content).
        """
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs, metadatas = [], []

        for title, content in res_list:
            chunks = text_splitter.split_text(content)
            for chunk in chunks:
                docs.append(chunk)
                metadatas.append({"title": title})

        vectorstore = FAISS.from_texts(docs, self.embeddings, metadatas=metadatas)
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir)
        vectorstore.save_local(self.index_dir)
        print(f"FAISS index saved to {self.index_dir}")

    def load_pipeline(self):
        """
        Loads the RAG pipeline from the saved FAISS index.
        
        Returns:
            RetrievalQA: RAG pipeline ready for queries.
        """
        if not os.path.exists(self.index_dir):
            raise FileNotFoundError(f"FAISS index directory '{self.index_dir}' not found.")

        vectorstore = FAISS.load_local(self.index_dir, self.embeddings, allow_dangerous_deserialization=True)

        llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=self.openai_api_key, temperature=0)

        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})  # Retrieve top 5 documents
        qa_pipeline = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True
        )

        print(f"RAG pipeline loaded from {self.index_dir}")
        return qa_pipeline

    def update_index(self, res_list):
        """
        Updates the FAISS index with new data.
        
        Args:
            res_list (list): List of tuples (title, content).
        """
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs, metadatas = [], []

        for title, content in res_list:
            chunks = text_splitter.split_text(content)
            for chunk in chunks:
                docs.append(chunk)
                metadatas.append({"title": title})

        if os.path.exists(self.index_dir):
            vectorstore = FAISS.load_local(self.index_dir, self.embeddings, allow_dangerous_deserialization=True)
            vectorstore.add_texts(docs, metadatas=metadatas)
        else:
            vectorstore = FAISS.from_texts(docs, self.embeddings, metadatas=metadatas)

        vectorstore.save_local(self.index_dir)
        print(f"FAISS index updated and saved to {self.index_dir}")
