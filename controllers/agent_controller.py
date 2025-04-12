from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from sqlalchemy.orm import Session
import json
from typing import List, Dict, Any
from services.files_service import FilesService

class AgentController:
    def __init__(self, files_service: FilesService, db: Session ):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )
        self.files_service = files_service
        self.db = db
        
    def create_examples(self) -> List[Dict[str, any]]:
        results = self.db.execute('SELECT input, output FROM examples')

        return [
            {
                "input": json.loads(row[0]),
                "output": json.loads(row[1])
            }
            for row in results
        ] 
    
    def create_main_prompt(self) -> ChatPromptTemplate:
        examples = self.create_examples()

        example_prompt = ChatPromptTemplate([
            ('human', '{input}'),
            ('ai', '{output}')
        ])

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples
        )

        return ChatPromptTemplate.from_messages([
            ('system', """You are a data transformation assistant. Convert the input data into the standardized JSON format. 
             Maintain the same structure as the examples, only changing the values."""),
            few_shot_prompt,
            ('human', '{input}')
        ])
    
    async def convert_to_json(self, rows: List[List[str]]) -> List[Dict[str, Any]]:
        main_prompt = self.create_main_prompt()
        
        chain = main_prompt | self.model

        results = []
        for row in rows:
            try:
                input = json.dumps(row[0])
                response = await chain.invoke({'input': input})
                results.append(response)

            except Exception as e:
                results.append({
                    "error": str(e),
                    "input": row
                })
        
        return results      



