# PDFChatApp 📚

Chat with your PDFs! **PDFChatApp** is a powerful, user-friendly Flask-based web application that lets you upload multiple PDF documents and interactively query their content. Leveraging **Langchain**, **OpenRouter**, and advanced NLP tools, PDFChatApp transforms your PDFs into a searchable, conversational knowledge base.

---

## ✨ Features

- **Upload Multiple PDFs**  
  Effortlessly upload one or more PDF files in a single session.

- **Robust Text Extraction**  
  Accurately extracts and processes text from a wide range of PDF documents.

- **Intelligent Q&A**  
  Ask natural language questions about your uploaded PDFs and receive contextually relevant answers.

- **Persistent Conversation History**  
  Maintains a session-based chat history for seamless, continuous conversations.

- **Isolated Session Management**  
  Each user session is private and independent—multiple users can interact simultaneously without interference.

- **Responsive, Modern UI**  
  Built with Tailwind CSS for a sleek, mobile-friendly interface.

- **Citations & References**  
  *(Optional: If implemented)* Answers can reference the source PDF and page number for easy verification.

- **Secure File Handling**  
  Uploaded files are handled securely and are not shared between users.

---

## 🛠️ Technologies Used

- **Flask**  
  Lightweight web framework for Python.

- **PyPDF2**  
  For extracting and parsing text from PDF files.

- **Langchain**  
  Framework for building LLM-powered applications:
    - `CharacterTextSplitter`: Splits extracted text into manageable chunks.
    - `HuggingFaceEmbeddings`: Generates vector embeddings from text.
    - `FAISS`: Enables fast similarity search in vector spaces.
    - `ConversationalRetrievalChain`: Powers the conversational Q&A experience.

- **OpenAI (via OpenRouter)**  
  Provides the Large Language Model backend for generating intelligent responses.

- **python-dotenv**  
  Manages environment variables securely.

- **Tailwind CSS**  
  Utility-first CSS framework for rapid UI development.

- **Node.js & npm**  
  For managing frontend build tools (Tailwind/PostCSS).

---

## Mermaid Diagram

```mermaid
flowchart TB
    %% Client Layer
    subgraph "Client (Browser UI)"
        direction TB
        IndexPage["index.html"]:::frontend
        UploadPage["upload.html"]:::frontend
        ChatPage["chat.html"]:::frontend
        InputCSS["input.css"]:::frontend
        OutputCSS["output.css"]:::frontend
    end

    %% Backend Layer
    subgraph "Backend (Flask App)":::logic
        direction TB
        App_py["app.py"]:::logic
        HtmlTemplates["htmltemplates.py"]:::logic

        subgraph "PDF Processing & Embeddings"
            direction TB
            TextExtraction["Text Extraction (PyPDF2)"]:::logic
            Chunking["Chunking (Langchain)"]:::logic
            Embedding["Embedding (HuggingFace)"]:::logic
            FAISSStore["FAISS Vector Store"]:::storage
            TextExtraction --> Chunking --> Embedding --> FAISSStore
        end

        subgraph "Retrieval & LLM Service"
            direction TB
            RetrievalChain["ConversationalRetrievalChain"]:::logic
            LLMCall["OpenRouter API Call"]:::logic
        end

        SessionStore["Flask Session Store"]:::storage
        FileStorage["faiss_index files"]:::storage
    end

    %% External Service
    OpenRouter["OpenRouter LLM Service"]:::external

    %% Build & Deployment
    subgraph "Build & Deployment":::config
        direction TB
        Makefile["Makefile"]:::config
        RenderCfg["render.yaml"]:::config
        PackageJSON["package.json"]:::config
        PackageLock["package-lock.json"]:::config
        TailwindCfg["tailwind.config.js"]:::config
        PostCSSCfg["postcss.config.js"]:::config
        Requirements["requirements.txt"]:::config
    end

    %% Data Flows
    IndexPage -->|loads| App_py
    UploadPage -->|POST /upload| App_py
    ChatPage -->|GET/POST /chat| App_py

    InputCSS --> IndexPage
    InputCSS --> UploadPage
    InputCSS --> ChatPage
    OutputCSS --> IndexPage
    OutputCSS --> UploadPage
    OutputCSS --> ChatPage

    App_py -->|invoke| TextExtraction
    App_py -->|invoke| RetrievalChain
    RetrievalChain -->|queries| FAISSStore
    RetrievalChain -->|calls| LLMCall
    LLMCall -->|API request| OpenRouter
    OpenRouter -->|API response| RetrievalChain
    RetrievalChain -->|send reply| ChatPage

    FAISSStore -->|persist| FileStorage
    App_py -->|session data| SessionStore

    %% Click Events
    click IndexPage "https://github.com/frosty-8/pdf-chatbot/blob/main/templates/index.html"
    click UploadPage "https://github.com/frosty-8/pdf-chatbot/blob/main/templates/upload.html"
    click ChatPage "https://github.com/frosty-8/pdf-chatbot/blob/main/templates/chat.html"
    click InputCSS "https://github.com/frosty-8/pdf-chatbot/blob/main/static/css/input.css"
    click OutputCSS "https://github.com/frosty-8/pdf-chatbot/blob/main/static/css/output.css"
    click App_py "https://github.com/frosty-8/pdf-chatbot/blob/main/app.py"
    click HtmlTemplates "https://github.com/frosty-8/pdf-chatbot/blob/main/htmltemplates.py"
    click TextExtraction "https://github.com/frosty-8/pdf-chatbot/blob/main/app.py"
    click RetrievalChain "https://github.com/frosty-8/pdf-chatbot/blob/main/app.py"
    click LLMCall "https://github.com/frosty-8/pdf-chatbot/blob/main/app.py"
    click SessionStore "https://github.com/frosty-8/pdf-chatbot/blob/main/app.py"
    click FileStorage "https://github.com/frosty-8/pdf-chatbot/blob/main/faiss_index/index.faiss"
    click Makefile "https://github.com/frosty-8/pdf-chatbot/tree/main/Makefile"
    click RenderCfg "https://github.com/frosty-8/pdf-chatbot/blob/main/render.yaml"
    click PackageJSON "https://github.com/frosty-8/pdf-chatbot/blob/main/package.json"
    click PackageLock "https://github.com/frosty-8/pdf-chatbot/blob/main/package-lock.json"
    click TailwindCfg "https://github.com/frosty-8/pdf-chatbot/blob/main/tailwind.config.js"
    click PostCSSCfg "https://github.com/frosty-8/pdf-chatbot/blob/main/postcss.config.js"
    click Requirements "https://github.com/frosty-8/pdf-chatbot/blob/main/requirements.txt"

    %% Styles
    classDef frontend fill:#ADD8E6,stroke:#333,stroke-width:1px
    classDef logic fill:#90EE90,stroke:#333,stroke-width:1px
    classDef storage fill:#FFA500,stroke:#333,stroke-width:1px,shape=cylinder
    classDef external fill:#DDA0DD,stroke:#333,stroke-width:1px
    classDef config fill:#F0E68C,stroke:#333,stroke-width:1px
```


## 🚀 Getting Started

Follow these steps to set up and run PDFChatApp locally.

### Prerequisites

- Python 3.8+
- `pip` (Python package installer)
- Node.js & npm (for frontend assets, only if you modify styles)

### Installation

1. **Clone the Repository**
    ```
    git clone <repository_url>
    cd <repository_name>
    ```

2. **Create and Activate a Virtual Environment**
    ```
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3. **Install Python Dependencies**
    ```
    pip install -r requirements.txt
    ```

4. **(Optional) Install Frontend Dependencies**
    If you plan to modify the CSS/UI:
    ```
    npm install
    ```

---

### Environment Variables

Create a `.env` file in the root directory with the following content:

```bash
OPENROUTER_API_KEY="your_openrouter_api_key_here"
YOUR_SITE_URL="http://127.0.0.1:5000" # Or your deployed site URL
YOUR_SITE_NAME="PDFChatApp" # A descriptive name for your application
```


- Obtain your `OPENROUTER_API_KEY` from [OpenRouter](https://openrouter.ai/).

---

### Running the Application

1. **Start the Flask App**
    ```
    python app.py
    ```
    Or use the Makefile:
    ```
    make run
    ```
    The app will be available at `http://127.0.0.1:5000/`.

2. **Build Tailwind CSS (if you modify `input.css`)**
    ```
    npm run build-css
    ```
    The `build-css` script includes `--watch` for automatic recompilation.

---

## 💡 Usage

1. **Upload PDFs**  
   Go to the home page (`/`) and upload one or more PDF documents.

2. **Processing**  
   The app extracts and processes text, creating a searchable knowledge base.

3. **Chat & Ask Questions**  
   Once processing is done, you'll be redirected to the chat page. Ask questions about your PDFs and get instant answers.

4. **View Conversation History**  
   Scroll through your chat to see previous questions and answers.

5. **Reset Session / Upload New PDFs**  
   Click "Upload a Different PDF" to clear your session and start over.

---

## 🧹 Cleaning Up

To remove the virtual environment and compiled Python files:

```bash
make clean
```


---

## 📝 Advanced Tips & Notes

- **Scaling**:  
  For production, consider using a production-ready WSGI server (e.g., Gunicorn) and configuring secure file storage.

- **Customization**:  
  You can easily extend the UI or backend logic to support additional file types, answer formatting, or citation features.

- **Security**:  
  Uploaded PDFs are processed per session and not shared. For sensitive data, ensure your deployment environment is secure.

- **Performance**:  
  For large documents or many concurrent users, consider using persistent vector stores and optimizing embedding/model calls.

---

## 🤝 Contributing

Pull requests and feature suggestions are welcome! Please open an issue or submit a PR for improvements.

---

## 📄 License

[MIT License](LICENSE)

---

## 📬 Support & Contact

For questions, issues, or feature requests, please open an issue on the repository or contact the maintainer.

---

Happy chatting with your PDFs! 🚀
