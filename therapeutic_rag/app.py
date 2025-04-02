import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
import streamlit as st

# Initial setup
MODEL = "gpt-4o"
db_name = "vector_db"

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'your-key-if-not-using-env')

# Read in documents using LangChain's loaders
folders = glob.glob("guidelines")

def add_metadata(doc, doc_type):
    doc.metadata["doc_type"] = doc_type
    return doc

text_loader_kwargs = {'encoding': 'utf-8'}

documents = []
for folder in folders:
    doc_type = os.path.basename(folder)
    loader = DirectoryLoader(folder, glob="**/*.md", loader_cls=TextLoader, loader_kwargs=text_loader_kwargs)
    folder_docs = loader.load()
    documents.extend([add_metadata(doc, doc_type) for doc in folder_docs])

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(documents)

# Extract guideline names
doc_names = []
for file in os.listdir("guidelines"):
    doc_names.append(file.replace(".md", ""))

# Set up vector store
embeddings = OpenAIEmbeddings()

if os.path.exists(db_name):
    Chroma(persist_directory=db_name, embedding_function=embeddings).delete_collection()

vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=db_name)

# Set up conversation chain with system prompt
system_template = """You are an expert medical AI assistant specializing in infectious disease therapeutics and clinical guidelines. Your role is to provide accurate, evidence-based information from the medical guidelines provided.

Follow these principles when responding:

1. ACCURACY AND EVIDENCE:
   - Base all responses strictly on the provided guideline content
   - Cite specific sections and recommendations from the guidelines
   - If information is missing or unclear, explicitly state this
   - Never make assumptions or provide information not found in the guidelines

2. CLINICAL RECOMMENDATIONS:
   - Present treatment options in order of preference/strength of recommendation
   - Include essential details about:
     * Dosing and duration
     * Route of administration
     * Monitoring requirements
     * Treatment modifications for special populations
   - Highlight any contraindications or warnings

3. RESPONSE STRUCTURE:
   - Begin with the primary recommendation or answer
   - Provide supporting details and evidence
   - Include relevant alternatives or exceptions
   - End with any important monitoring or follow-up points

4. SAFETY AND SCOPE:
   - Emphasize that recommendations come from guidelines and may need clinical judgment
   - Note if recommendations are setting-specific (e.g., outpatient vs. inpatient)
   - Highlight any critical warnings or precautions
   - Indicate when consultation with a specialist is recommended

5. If the question is not about a guideline, say that you are not sure about the answer.

6. You should respond with the First line treatment, notes and alternative if first line treatment is not available.


Context: {context}
Question: {question}

Provide a clear, structured response following the principles above."""

messages = [
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template("{question}")
]
prompt = ChatPromptTemplate.from_messages(messages)

# Set up conversation chain
llm = ChatOpenAI(temperature=0, model_name=MODEL)
memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
retriever = vectorstore.as_retriever()
conversation_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    combine_docs_chain_kwargs={'prompt': prompt}
)

# Streamlit UI
st.set_page_config(
    page_title="Medical Guidelines RAG",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state for chat history only
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Main UI
st.title("🏥 Medical Guidelines Assistant")
st.write("An AI-powered assistant for querying medical guidelines using retrieval-augmented generation")

# Sidebar with available guidelines
with st.sidebar:
    st.header("Available Guidelines")
    if doc_names:
        st.write("Currently loaded guidelines:")
        for name in doc_names:
            st.markdown(f"- {name}")
    else:
        st.warning("No guidelines found in the 'guidelines' directory")

# Main chat interface
st.markdown("### 💬 Ask about Medical Guidelines")

# Display chat history
for message in st.session_state.chat_history:
    role = "🤖 Assistant" if message["role"] == "assistant" else "👤 You"
    st.markdown(f"**{role}**: {message['content']}")

# Query input
query = st.text_input("Enter your question about the guidelines:", key="query_input")

if st.button("Ask"):
    if query:
        with st.spinner("Searching guidelines..."):
            # Get response from conversation chain
            response = conversation_chain.invoke({"question": query})
            
            # Add to chat history
            st.session_state.chat_history.append({"role": "user", "content": query})
            st.session_state.chat_history.append({"role": "assistant", "content": response["answer"]})
            
            # Clear input
            st.rerun()

# Clear chat history button
if st.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.rerun()

    

