from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings,ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv

load_dotenv()

# indexign phase-------------------------------

# load document
loader = PyPDFLoader('nodejs.pdf')
docs = loader.load()

# step 1 - splitte

text_spliter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

split_doc = text_spliter.split_documents(docs)


# step 2 - embedding

embedder = OpenAIEmbeddings(
    model="text-embedding-3-large",
)

# step 3 - vector store

vector_store = QdrantVectorStore.from_documents(
    documents=[],
    url="http://localhost:6333",
    collection_name="learning_langchain",
    embedding=embedder
)


print('enjection done')

# Retreival phase --------------------------------------------

# step 4 - semantic search

retrivel = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_langchain",
    embedding=embedder
)

# step 5 - reterived document

query = input("enter the query > ")

retrival_result = retrivel.similarity_search(
    query=query
)

print(retrival_result)

print("🧠 reterived the document")

# step 6 - genration phase ---------------------------

page_content = ''

for obj in retrival_result:
    page_content += obj.page_content

# step 6 - send query with Reterived doc. to GPT

chat_prompt = ChatPromptTemplate([
    ('system', 'You are an assistant helping to answer user queries based on the following content. If the answer to the query is not found in the content, respond with: "This query is not present in the document." Here is the content:\n\n{page_content}'),
    ('human', 'Explain in simple terms: what is {query}?')
])


prompt = chat_prompt.invoke({"page_content":page_content,"query":query})

model = ChatOpenAI(
    model="gpt-4o-mini"
)

res = model.invoke(prompt)

print(res.content)