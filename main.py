from langchain_groq import ChatGroq
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from controllers.agent_controller import AgentController
from services.files_service import FilesService
from config.database import get_db


app = FastAPI()

@app.post("/process", response_class=JSONResponse)
async def process_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        if not file.filename.endswith((".csv", ".xlsx", ".xls")):
            raise HTTPException(400, "File must be csv, xlsx, or xls")
        
        content = await file.read()
        model = ChatGroq(
            model="llama-3.2-11b-vision-preview",
            temperature=0.0,
            max_retries=2
        )
        files_service = FilesService()
        agent_controller = AgentController(model, files_service, db)

        rows = files_service.parse_file(file.filename, content)
        results = await agent_controller.convert_to_json(rows)

        return {
            "filename": file.filename,
            "success_count": len([row for row in results if "error" not in row]),
            "error_count": len([row for row in results if "error" in row]),
            "results": results
        }
    
    except Exception as e:
        print(e)
        raise HTTPException(500, "Unable to process request at this time")        

       

