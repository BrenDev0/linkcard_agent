from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from sqlalchemy.orm import Session
import json
from typing import List, Dict, Any
from services.files_service import FilesService
from sqlalchemy import text
import ast


class LinkCardParser:
    def __init__(self, model,  files_service: FilesService, db: Session ):
        self.model = model
        self.files_service = files_service
        self.db = db
        
    def create_examples(self) -> List[Dict[str, any]]:
        results = self.db.execute(text("SELECT input, output FROM examples"))
        rows = results.fetchall()

        data = []
        for i, row in enumerate(rows):  # Use enumerate to track the row index
            try:
                data.append({
                    "input": json.loads(row[0]),
                    "output": json.loads(row[1])
                })
            except json.JSONDecodeError as e:
                print(f"\n🚨 JSON Decode Error at row {i}: {e}")
                print(f"🔎 Input: {row[0]}")
                print(f"🔎 Output: {row[1]}")
                # Use continue to keep processing other rows
                continue 

        return data     
    
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
            ('system', """You are a precise and expert data entry assistant.

            Your task is to transform user input into a structured array of JSON objects that strictly match the format and field structure demonstrated in the examples.

            Instructions:
            - Only use the fields shown in the examples. Do not add or infer new fields.
            - Do not generate any placeholder or default values.
            - If no suitable value exists in the input for a required field, assign it as null.
            - Use your best judgment to map the input data to the correct fields in the output.
            - Return only the JSON array—no explanations, no extra text.
            - Your response must strictly follow the structure, naming, and formatting of the example outputs.

            Your response will always be a raw array of JSON objects."""),
            few_shot_prompt,
            ('human', '{input}')
        ])
    
    
    
    async def convert_to_json(self, rows: List[List[str]]) -> List[Dict[str, Any]]:
        main_prompt = self.create_main_prompt()
        
        chain = main_prompt | self.model

        results = []
        for row in rows:
            try:
                input = {'input': row}
                response = chain.invoke(input) 
                results.append(json.loads(response.content))
                

            except Exception as e:
                results.append({
                    "error": str(e),
                    "input": row
                })

        return results
       
        return    



