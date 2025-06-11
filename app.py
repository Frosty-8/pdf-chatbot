from flask import Flask, render_template, request, session, flash, redirect, url_for
import io
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError, EmptyFileError
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.chains import ConversationalRetrievalChain
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langchain_core.outputs import ChatResult, ChatGeneration, Generation
from openai import OpenAI
from pydantic import BaseModel, Field
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
YOUR_SITE_URL = os.getenv("YOUR_SITE_URL", "http://127.0.0.1:5000")
YOUR_SITE_NAME = os.getenv("YOUR_SITE_NAME", "PDFChatApp")

# In-memory chat history (use a database in production)
message_histories = {}

def get_session_id():
    return session.get('session_id', 'default')

# Custom LLM for OpenRouter
class OpenRouterLLM(BaseChatModel, BaseModel):
    client: OpenAI = Field(default=None)
    model: str = Field(default="deepseek/deepseek-r1-zero:free")

    def __init__(self):
        super().__init__()
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )

    def _convert_message(self, message: BaseMessage) -> dict:
        return {
            "role": "user" if isinstance(message, HumanMessage) else "assistant",
            "content": message.content
        }

    def _generate(self, messages: list[BaseMessage], stop: list[str] = None) -> ChatResult:
        message_dicts = [self._convert_message(msg) for msg in messages]
        completion = self.client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": YOUR_SITE_URL,
                "X-Title": YOUR_SITE_NAME,
            },
            model=self.model,
            messages=message_dicts,
            stop=stop
        )
        response_content = completion.choices[0].message.content
        # Create a ChatGeneration with the response
        generation = ChatGeneration(
            message=AIMessage(content=response_content),
            generation_info={"finish_reason": "stop"}
        )
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "openrouter"

def process_pdf(pdf_docs):
    text = ""
    valid_pdfs = 0
    for pdf in pdf_docs:
        content = pdf.read()
        if not content:
            flash(f"Skipping empty file: {pdf.filename}", "warning")
            continue
        pdf.stream.seek(0)
        try:
            pdf_reader = PdfReader(io.BytesIO(content))
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            valid_pdfs += 1
        except (PdfReadError, EmptyFileError) as e:
            flash(f"Error processing {pdf.filename}: {str(e)}", "warning")
    if not valid_pdfs:
        flash("No valid PDFs were processed.", "warning")
        return None, 0
    if not text.strip():
        flash("No text could be extracted from the PDFs.", "warning")
        return None, 0
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len)
    text_chunks = text_splitter.split_text(text)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore, valid_pdfs

def get_conversation_chain(vectorstore):
    llm = OpenRouterLLM()
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        return_source_documents=True
    )

@app.route("/", methods=["GET", "POST"])
def upload():
    if 'vectorstore_path' in session:
        return redirect(url_for('chat'))

    if request.method == "POST":
        pdf_docs = request.files.getlist('pdf_docs')
        pdf_docs = [pdf for pdf in pdf_docs if pdf.filename]
        if not pdf_docs:
            flash("No files were selected.", "warning")
            return redirect(url_for('upload'))
        vectorstore, valid_pdfs = process_pdf(pdf_docs)
        if not vectorstore:
            return redirect(url_for('upload'))
        vectorstore_path = "faiss_index"
        vectorstore.save_local(vectorstore_path)
        session['vectorstore_path'] = vectorstore_path
        session['session_id'] = os.urandom(16).hex()
        session.modified = True
        flash(f"Processed {valid_pdfs} PDF(s) successfully! Proceed to ask questions.", "success")
        return redirect(url_for('chat'))

    return render_template("upload.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if 'vectorstore_path' not in session:
        flash("Please upload a PDF first.", "warning")
        return redirect(url_for('upload'))

    if request.method == "POST":
        user_question = request.form.get('user_question', '').strip()
        if user_question:
            vectorstore = FAISS.load_local(
                session['vectorstore_path'],
                embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
                allow_dangerous_deserialization=True
            )
            chain = get_conversation_chain(vectorstore)
            message_history = message_histories.get(get_session_id(), ChatMessageHistory())
            conversational_chain = RunnableWithMessageHistory(
                chain,
                lambda session_id: message_history,
                input_messages_key="question",
                history_messages_key="chat_history",
                output_messages_key="answer"
            )
            response = conversational_chain.invoke(
                {"question": user_question},
                config={"configurable": {"session_id": get_session_id()}}
            )
            message_histories[get_session_id()] = message_history
            return render_template("chat.html", chat_history=message_history.messages, latest_response=response['answer'])
        flash("Please enter a valid question.", "warning")

    message_history = message_histories.get(get_session_id(), ChatMessageHistory())
    return render_template("chat.html", chat_history=message_history.messages, latest_response=None)

@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    message_histories.clear()
    flash("Session reset. Please upload a new PDF.", "success")
    return redirect(url_for('upload'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)