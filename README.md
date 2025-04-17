
# Chromium Android Assistant

An AI-powered assistant to help developers understand and navigate the Chromium Android codebase. It uses RAG (Retrieval-Augmented Generation) with Ollama for local LLM processing.

## Prerequisites

- Python 3.11+
- Node.js 16+
- Ollama installed on your system
- Chromium source code

## Installation

### 1. Clone Chromium Source
```bash
# Clone Chromium Android source
fetch --nohooks android
gclient sync -D
```

### 2. Setup Backend

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/MacOS
# OR
.venv\Scripts\activate     # On Windows

# Install dependencies
pip install langchain-community langchain-ollama langchain-chroma fastapi uvicorn

# Install embedding model dependencies
pip install sentence-transformers
```

### 3. Setup Ollama and Model

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull CodeLlama model (recommended for code understanding)
ollama pull codellama
# or
ollama pull mixtral

# Create custom model for Chromium
cat > Modelfile << 'EOF'
FROM codellama

SYSTEM """You are a Chromium Android development expert. 
You help developers understand the codebase and implement features.
Always reference specific files and code when answering.
You can communicate in both English and Thai."""

PARAMETER temperature 0.7
PARAMETER top_p 0.9
EOF

# Create the custom model
ollama create chromium-assistant -f Modelfile
```

### 4. Setup Frontend

```bash
# Create and setup frontend
cd frontend
npm install
```

## Indexing the Codebase

Create an indexing script (`index_code.py`):

```python
import os
from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings 
from langchain_community.vectorstores import Chroma

# Android-specific paths
ANDROID_PATHS = [
    "./chromium/src/android_webview",
    "./chromium/src/chrome/android",
    "./chromium/src/content/public/android",
    "./chromium/src/base/android",
]

# Collect documents
documents = []
for path in ANDROID_PATHS:
    loader = DirectoryLoader(
        path,
        glob="**/*.[ch]*",  # Include .c, .h, .cc, .cpp, .java
        loader_cls=TextLoader
    )
    documents.extend(loader.load())

# Split documents
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
splits = splitter.split_documents(documents)

# Create embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Store in Chroma
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="./chromium_db"
)
```

Run the indexing:
```bash
python index_code.py
```

## Development

1. Start the backend:
```bash
# Activate virtual environment
source .venv/bin/activate

# Start backend server
uvicorn main:app --reload
```

2. Start the frontend development server:
```bash
# In another terminal
cd frontend
npm run dev
```

The development server will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## Production Deployment

### Backend

1. Install production dependencies:
```bash
pip install gunicorn
```

2. Run with Gunicorn:
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend

1. Build the frontend:
```bash
cd frontend
npm run build
```

2. Serve the built files using a web server like Nginx.

Example Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## System Requirements

- RAM: 16GB+ recommended (8GB minimum)
- Storage: 
  - ~20GB for Chromium source
  - ~4GB for CodeLlama model
  - ~2GB for vector store
- GPU: Optional but recommended for better performance

## Troubleshooting

1. If Ollama fails to load, check:
   - Ollama service is running
   - Model is properly installed
   - System has enough RAM

2. If indexing fails:
   - Check source code paths exist
   - Ensure enough disk space
   - Try reducing chunk size

3. If frontend can't connect to backend:
   - Check CORS settings in backend
   - Verify API endpoint URLs
   - Check network connectivity

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details
# chromium-dev-ai
# chromium-dev-ai
# chromium-dev-ai
