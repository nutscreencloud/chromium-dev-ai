import os
import glob
from pathlib import Path
from typing import List, Optional, Any
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Define paths for Android
ANDROID_PATHS = [
    "/home/nut/Code/chromium-builder/chromium/src/android_webview",
    "/home/nut/Code/chromium-builder/chromium/src/chrome/android",
    "/home/nut/Code/chromium-builder/chromium/src/content/public/android",
    "/home/nut/Code/chromium-builder/chromium/src/base/android",
]

# Define file extensions to process
TEXT_EXTENSIONS = {
    '.java', '.c', '.h', '.cc', '.cpp', '.py', '.js', '.html', 
    '.css', '.xml', '.txt', '.md', '.sh', '.build', '.gn'
}

class SafeTextLoader(TextLoader):
    def load(self):
        ext = os.path.splitext(self.file_path)[1].lower()
        if ext not in TEXT_EXTENSIONS:
            return []
        try:
            return super().load()
        except Exception:
            return []

class SafeDirectoryLoader(DirectoryLoader):
    def __init__(
        self,
        path: str,
        glob: str = "**/[!.]*",
        loader_cls: Any = TextLoader,
        loader_kwargs: Optional[dict] = None,
        recursive: bool = True,
        use_multithreading: bool = False,
        max_concurrency: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            path,
            glob=glob,
            loader_cls=loader_cls,
            loader_kwargs=loader_kwargs or {},
            recursive=recursive,
            use_multithreading=use_multithreading,
            max_concurrency=max_concurrency,
            **kwargs,
        )

    def iter_files(self) -> List[str]:
        """Recursively get all files in the directory that match the glob pattern."""
        paths = []
        for file_path in glob.glob(os.path.join(self.path, self.glob), recursive=self.recursive):
            if os.path.isfile(file_path):
                paths.append(file_path)
        return paths

    def load(self) -> List:
        """Load documents."""
        docs = []
        for file_path in self.iter_files():
            if os.path.splitext(file_path)[1].lower() in TEXT_EXTENSIONS:
                try:
                    loader = self.loader_cls(file_path, **self.loader_kwargs)
                    sub_docs = loader.load()
                    docs.extend(sub_docs)
                except Exception:
                    pass
        return docs

def load_documents(paths):
    documents = []
    for path in paths:
        try:
            loader = SafeDirectoryLoader(
                path,
                glob="**/*",
                loader_cls=SafeTextLoader,
                use_multithreading=True,
                loader_kwargs={'encoding': 'utf-8'}
            )
            path_docs = loader.load()
            if path_docs:
                print(f"Loaded {len(path_docs)} documents from {path}")
                documents.extend(path_docs)
        except Exception as e:
            print(f"Error processing directory {path}: {str(e)}")
    return documents

# Load and process documents
documents = load_documents(ANDROID_PATHS)

if not documents:
    print("No documents were successfully loaded. Exiting.")
    exit(1)

print(f"Total documents loaded: {len(documents)}")

# Create text chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
chunks = text_splitter.split_documents(documents)

if not chunks:
    print("No text chunks were created after splitting. Exiting.")
    exit(1)

print(f"Created {len(chunks)} text chunks")

# Create embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Store in Chroma
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chromium_db"
)