import os
from pathlib import Path
import shutil
import tempfile
from PIL import Image
import streamlit as st
from langchain.llms import LlamaCpp
from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader, ServiceContext

# Constants
GGUF_FILE_NAME = "neuralbeagle14-7b.Q5_K_M.gguf"
SCRIPT_DIR = Path(__file__).resolve().parent
MODEL_PATH = SCRIPT_DIR / "models" / GGUF_FILE_NAME
if not MODEL_PATH.exists():
    print("Please download the gguf file using `python3 download_neural_beagle.py`")

# LLM Initialization
def set_llm(n_ctx: int = 4096, temperature: float = 0.0, max_tokens: int = 2048):
    return LlamaCpp(
        model_path=str(MODEL_PATH),
        n_batch=512,
        n_gpu_layers=2,
        f16_kv=True,
        verbose=True,
        n_ctx=n_ctx,  # Max 4096
        top_k=10,
        top_p=0.95,
        repeat_penalty=1.1,
        temperature=temperature,
        seed=42,
        max_tokens=max_tokens  # Can be smaller
    )

# Global LLM Instance (singleton pattern)
LLM_INSTANCE = set_llm()

# System prompts
system_prompt_fr = "Tu es un assistant serviable, très qualifié et qui s'exprime en français. Exécute les instructions suivantes au mieux de tes capacités. Tu donneras des réponses exactes et concises.\n" 
system_prompt_en = "You are a very helpful assistant. Perform the following instructions to the best of your ability.You always give your answers in English with a good writing style.\n"

qa_system_prompt_fr = system_prompt_fr
qa_system_prompt_en = system_prompt_en

qa_prompt_template = """{system_prompt}.\n
### Instruction:{query}
### Response :

"""

def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='-' + uploaded_file.name, mode='wb+') as temp_file:
            shutil.copyfileobj(uploaded_file, temp_file)
            return temp_file.name
    return None

def get_qa_system_answer(query, language):
    system_prompt = qa_system_prompt_fr if language.lower().startswith("fra") else qa_system_prompt_en
    prompt = qa_prompt_template.format(system_prompt=system_prompt, query=query)
    answer = LLM_INSTANCE(prompt=prompt)
    return answer or "Oops! No result found"

def get_document_based_response(query, file_path, language):
    if not os.path.exists(file_path):
        return f"Not a valid file: {file_path}"

    system_prompt = system_prompt_fr if language.lower().startswith("fra") else system_prompt_en
    context_window, num_output, chunk_overlap = 2048, 1024, 20
    documents = SimpleDirectoryReader(input_files=[file_path]).load_data() if os.path.isfile(file_path) else SimpleDirectoryReader(file_path).load_data()
    service_context = ServiceContext.from_defaults(llm=LLM_INSTANCE, system_prompt=system_prompt, context_window=context_window, chunk_overlap=chunk_overlap, num_output=num_output, embed_model="local")
    index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)
    response = index.as_query_engine().query(query)
    return response or "Oops! No result found"

# Streamlit UI Code
def setup_streamlit_ui():
    col1, col2, col3 = st.columns([3, 4, 1])

    with col2:
        st.title("ChatDoc+")
        st.image(Image.open(SCRIPT_DIR / "imgs" / "llama_ai.png"), use_column_width=False)

    uploaded_file = st.file_uploader(label="Drag and Drop your file here", key='file_uploader', label_visibility="hidden")
    language = st.sidebar.selectbox(label="Response Language", options=["English", "Français"])
    temp_file_path = save_uploaded_file(uploaded_file)

    with st.sidebar:
        if temp_file_path:
            st.markdown(f"<h4>Current document: {uploaded_file.name}</h4>", unsafe_allow_html=True)
            query_prompt = "What would you like to ask about this document?"
        else:
            st.write("No document provided: Chat mode")
            query_prompt = "Ask any question, or drag and drop a document and chat with it."

    if 'query_submitted' not in st.session_state:
        st.session_state.query_submitted = False

    query = st.chat_input(placeholder=query_prompt)

    if query is not None:
        st.session_state.query_submitted = True

    if st.session_state.query_submitted and query:
    # Display the user's query
        with st.chat_message(name="Q"):
            st.write(query)

        # Try processing the query based on file upload
        try:
            answer = get_qa_system_answer(query, language) if not uploaded_file else get_document_based_response(query, temp_file_path, language)
            with st.chat_message(name="A"):
                st.success(answer)
        except Exception as e:
            st.error(f"An error occurred: {e}")

def main():
    setup_streamlit_ui()

if __name__ == "__main__":
    main()

