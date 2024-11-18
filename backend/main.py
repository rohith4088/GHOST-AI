# import os
# import tempfile
# from dotenv import load_dotenv
# from langchain import PromptTemplate, LLMChain
# from langchain.llms import OpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI
# from config import WHITE, GREEN, RESET_COLOR,model_name
# from utils import format_user_question
# from file_processing import clone_github_repo, load_and_index_files
# from questions import ask_question, QuestionContext
# from fastapi import FastAPI, Form, Request
# from fastapi.middleware.cors import CORSMiddleware


# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# def main():
#     github_url = input("Enter the GitHub URL of the repository: ")
#     repo_name = github_url.split("/")[-1]
#     print("Cloning the repository...")
#     with tempfile.TemporaryDirectory() as local_path:
#         if clone_github_repo(github_url, local_path):
#             index, documents, file_type_counts, filenames = load_and_index_files(local_path)
#             if index is None:
#                 print("No documents were found to index. Exiting.")
#                 exit()

#             print("Repository cloned. Indexing files...")
#             llm = ChatGoogleGenerativeAI(api_key=GEMINI_API_KEY, model=model_name)

#             template = """
#             Repo: {repo_name} ({github_url}) | Conv: {conversation_history} | Docs: {numbered_documents} | Q: {question} | FileCount: {file_type_counts} | FileNames: {filenames}

#             Instr:
#             1. Answer based on context/docs.
#             2. Focus on repo/code.
#             3. Consider:
#                 a. Purpose/features - describe.
#                 b. Functions/code - provide details/samples.
#                 c. Setup/usage - give instructions.
#             4. Unsure? Say "I am not sure".

#             Answer:
#             """

#             prompt = PromptTemplate(
#                 template=template,
#                 input_variables=["repo_name", "github_url", "conversation_history", "question", "numbered_documents", "file_type_counts", "filenames"]
#             )

#             llm_chain = LLMChain(prompt=prompt, llm=llm)

#             conversation_history = ""
#             question_context = QuestionContext(index, documents, llm_chain, model_name, repo_name, github_url, conversation_history, file_type_counts, filenames)
#             while True:
#                 try:
#                     user_question = input("\n" + WHITE + "Ask a question about the repository (type 'exit()' to quit): " + RESET_COLOR)
#                     if user_question.lower() == "exit()":
#                         break
#                     print('Thinking...')
#                     user_question = format_user_question(user_question)

#                     answer = ask_question(user_question, question_context)
#                     print(GREEN + '\nANSWER\n' + answer + RESET_COLOR + '\n')
#                     conversation_history += f"Question: {user_question}\nAnswer: {answer}\n"
#                 except Exception as e:
#                     print(f"An error occurred: {e}")
#                     break

#         else:
#             print("Failed to clone the repository.")





# app = FastAPI()

# import os

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[os.environ.get("CORS_ORIGIN", "http://localhost:3000")],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get('/')
# def read_root():
#     return {"message": "hello backend"}

# backend/main.py
# requirements.txt



from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import aioredis
import os
import json
import shutil
import uuid
from config import settings  # Assuming you have a config.py
from pack.project_analyzer import ProjectAnalyzer  # Import your analyzer class

app = FastAPI(
    title="Project Analyzer",
    description="API for analyzing code projects with AI insights",
    version="1.0.0"
)

# CORS configuration 
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "Content-Range"] 
)

# Initialize Redis
redis = aioredis.from_url(settings.REDIS_URL) 

# Create tmp directory if it doesn't exist
os.makedirs("./tmp", exist_ok=True)

@app.post("/analyze")
async def analyze_project(file: UploadFile = File(...), prompt: Optional[str] = None):
    """
    Handle project upload and analysis.
    """
    try:
        # Validate file size
        file_size = 0
        chunk_size = 1024 * 1024  # 1MB chunks

        # Create temporary directory for the project
        project_id = str(uuid.uuid4()) 
        project_path = f"./tmp/{project_id}"
        os.makedirs(project_path, exist_ok=True)

        # Save uploaded file in chunks
        file_path = os.path.join(project_path, file.filename)
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(chunk_size):
                file_size += len(chunk)
                if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024: 
                    shutil.rmtree(project_path)  # Cleanup on error
                    raise HTTPException(
                        status_code=413, 
                        detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB" 
                    )
                buffer.write(chunk)

        # Extract if it's a zip file
        if file.filename.endswith('.zip'):
            try:
                shutil.unpack_archive(file_path, project_path)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to extract ZIP file: {str(e)}")

        # Analyze the project
        analyzer = ProjectAnalyzer(project_path)  # Create an instance of your analyzer
        results = await analyzer.analyze_project() 

        # Cache the analysis results in Redis
        await redis.set(f"project:{project_id}", json.dumps(results)) 

        # Cleanup temporary files
        shutil.rmtree(project_path)  

        return {
            "project_id": project_id,
            "results": results
        }

    except HTTPException:
        raise  # Re-raise HTTPExceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

@app.get("/results/{project_id}")
async def get_results(project_id: str):
    """
    Retrieve cached analysis results from Redis.
    """
    results = await redis.get(f"project:{project_id}")
    if not results:
        raise HTTPException(status_code=404, detail="Results not found")
    return json.loads(results) 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)