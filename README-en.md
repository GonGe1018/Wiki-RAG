[**한국어**](./README.md)
[**English**](./README-en.md)

Please note that this README was translated by AI and might not be perfectly accurate.


# Wiki-RAG

This project crawls wiki data, summarizes it using OpenAI's GPT, and builds a RAG pipeline using FAISS indexes.

***Currently, only Namuwiki crawling is supported.***

---

## 📋 Features

1. **Wiki Crawling and Summarization**:
   - Crawl wiki data by providing a URL and document title.
   - Summarize the crawled data and save it.

2. **RAG Pipeline Construction**:
   - Create FAISS indexes from the crawled and summarized data.

3. **Question-Answer System**:
   - Load the FAISS index to answer user queries using `gpt-4o-mini` and provide the source of the answer.

---

## 📂 Project Structure

```plaintext
project/
├── app.py                 # Main Streamlit application file
├── crawler.py             # WikiCrawler implementation
├── summarizer.py          # OpenAISummarizer implementation
├── rag_pipeline.py        # RAG pipeline implementation
├── requirements.txt       # Required Python packages
└── README.md              # Project documentation
```

---

## 🛠️ Installation and Execution

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit App
```bash
streamlit run app.py
```

---

## 🖥️ How to Use

### 1. Enter OpenAI API Key

- After running the app, enter your OpenAI API key in the **sidebar**.

### 2. Execute Crawling and Summarization
Crawl the wiki using Selenium and summarize the content using OpenAI's API. The summarized data will be saved locally.
- **Inputs**:
  - **Crawling Start URL**: The starting URL for the crawling process. ***(Currently supports Namuwiki only.)***
  - **Starting Document Title**: The title of the document to start crawling.
  - **Crawling Depth**: The maximum depth to traverse.

### 3. Build the RAG Pipeline
Create a FAISS index to enable vector search using the crawled and summarized data.
- Enter the folder name (`dir_name`) containing the crawled data.
  - The folder name is generated automatically during the "Crawling and Summarization" step.
- Enter the path to save the RAG pipeline index.

### 4. Load the RAG Pipeline and Ask Questions
Load the constructed RAG pipeline to use it.
- Select a saved FAISS index from the dropdown menu.
- Input your question, and the system will provide an answer along with its source.

---

## 💡 Tips

1. **Crawling Depth**:
   - The higher the crawling depth, the longer it takes. For quick testing, set the depth to 1.

2. **OpenAI API Key**:
   - The API key is entered via the Streamlit UI, not hardcoded.

