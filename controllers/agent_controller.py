from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from sqlalchemy.orm import Session
import json
from typing import List, Dict, Any
from services.files_service import FilesService
from sqlalchemy import text
import ast


class AgentController:
    def __init__(self, model,  files_service: FilesService, db: Session ):
        self.model = model
        self.files_service = files_service
        self.db = db
        
    def create_examples(self) -> List[Dict[str, any]]:
        results = self.db.execute(text("SELECT input, output FROM examples"))

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
            ('system', """You are a data transformation assistant. 
              the input data into the standardized JSON format. 
             Maintain the same structure as the examples, only changing the values. 
             do not add any keys that do not appear in the examples. 
             there are no default values, if any key does not have a value the value will be null. 
             Do not explain anything just return the json results in valid json response format"""),
            few_shot_prompt,
            ('human', '{input}')
        ])
    
    
    
    async def convert_to_json(self, rows: List[List[str]]) -> List[Dict[str, Any]]:
        main_prompt = self.create_main_prompt()
        print("in json")
        
        chain = main_prompt | self.model

        results = []
        for row in rows:
            try:
                input = {'input': row}
                response = chain.invoke(input) 
                results.append(ast.literal_eval(response.content))
                print(results)

            except Exception as e:
                results.append({
                    "error": str(e),
                    "input": row
                })

        return results
       
        return    



