from pathlib import Path
from tqdm import tqdm
from transformers import AutoTokenizer
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores.utils import DistanceStrategy

def hf_embedding_internal(embedding_model_name: str) -> HuggingFaceEmbeddings:
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model_name
    )
    print(f"{embedding_model_name} loaded.")
    return embeddings

def build_index_internal(embedding_model_name, texts_dir_name, index_dir_name):
    # Load all text files from 'huaihai_texts' directory
    texts_dir = Path(texts_dir_name)
    source_docs = []

    if texts_dir.exists():
        for file_path in texts_dir.glob("*.txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                source_docs.append(
                    Document(
                        page_content=content, 
                        metadata={"source": file_path.name}
                    )
                )
        print(f"Loaded {len(source_docs)} text files from {texts_dir}")
    else:
        raise FileNotFoundError(f"Directory '{texts_dir}' not found")

    text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        AutoTokenizer.from_pretrained(embedding_model_name),
        chunk_size=200,
        chunk_overlap=20,
        add_start_index=True,
        strip_whitespace=True,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    # Split docs and keep only unique ones
    print("Splitting documents...")
    docs_processed = []
    unique_texts = {}
    for doc in tqdm(source_docs):
        new_docs = text_splitter.split_documents([doc])
        for new_doc in new_docs:
            if new_doc.page_content not in unique_texts:
                unique_texts[new_doc.page_content] = True
                docs_processed.append(new_doc)

    embedding_model = hf_embedding_internal(embedding_model_name)
    vectordb = FAISS.from_documents(
        documents=docs_processed,
        embedding=embedding_model,
        distance_strategy=DistanceStrategy.COSINE,
    )
    vectordb.save_local(index_dir_name)
    print(f"FAISS vectorstore saved to '{index_dir_name}' directory.")

def load_index_internal(embedding_model_name: str, index_dir_name: str) -> FAISS:
    embedding_model = hf_embedding_internal(embedding_model_name)
    vectordb = FAISS.load_local(index_dir_name, embedding_model, allow_dangerous_deserialization=True)
    print("Vectorstore loaded.")
    return vectordb

# embedding_model_name = "thenlper/gte-small-zh"
embedding_model_name = "./models/thenlper/gte-small-zh"
texts_dir_name = "texts"
index_dir_name = "faiss_index"

def build_index():
    build_index_internal(embedding_model_name, texts_dir_name, index_dir_name)

def load_index() -> FAISS:
    return load_index_internal(embedding_model_name, index_dir_name)

if __name__ == "__main__":
    print("Run this command will create FAISS index.")
    print(f"Source files: {texts_dir_name}/*.txt")
    print(f"FAISS index will be saved to: {index_dir_name}")
    print(f"Using embedding model: {embedding_model_name}")
    print("Do you want to continue? (y/n)")
    user_input = input().strip().lower()
    if user_input == "y":
        build_index()