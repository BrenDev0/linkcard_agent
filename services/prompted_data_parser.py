from fastapi import WebSocket
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from sqlalchemy.orm import Session
import json
from typing import List, Dict, Any
from sqlalchemy import text
import ast


class PromptedDataParser:
    def __init__(self, model, db: Session, websocket: WebSocket ):
        self.model = model
        self.db = db
        self.websocket = websocket
        
    def create_examples(self) -> List[Dict[str, any]]:
        results = self.db.execute(text("SELECT input, output FROM examples"))
        rows = results.fetchall()

        data = []
        for row in rows: 
            try:
                data.append({
                    "input": json.loads(row[0]),
                    "output": json.loads(row[1])
                })
            except json.JSONDecodeError as e:
                print(e)
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

            Your task is to transform user input into a structured JSON objects that strictly match the format and field structure demonstrated in the examples.

            Instructions:
            - Only use the fields shown in the examples. Do not add or infer new fields.
            - Do not generate any placeholder or default values.
            - If no suitable value exists in the input for a required field, assign it as null.
            - If none of the fields in the input match the expected structure, return false.
            - Use your best judgment to map the input data to the correct fields in the output.
            - Return only the JSON Objects like the output examples, no explanations, no extra text.
            - Your response must strictly follow the structure, naming, and formatting of the example outputs.

            Your response will always be either a JSON object or the literal value false."""),
            few_shot_prompt,
            ('human', '{input}')
        ])
    
    
    
    async def convert_to_json(self, rows: List[Dict[str, any]]) -> List[Dict[str, Any]]:
        main_prompt = self.create_main_prompt()
        
        chain = main_prompt | self.model

        for row in rows:
            try:
                input = {'input': row}
                response = await chain.ainvoke(input) 
                output = ast.literal_eval(response.content)
                if output.get("name") is None or output.get("phone") is None:
                    raise ValueError("Nombre y Teléfono son campos obligatorios.")
                
                if (output.get("name") in [None, "Nombre", "nombre", "name", "Name"]):
                    raise ValueError("Expected row with data but recieved header") 


                if self.websocket:
                    await self.websocket.send_json(output)
        
                else:
                    print("No websocket connected.")          

            except Exception as e:
                error_payload = {
                    "error": str(e),
                    "input": row
                }

                if self.websocket:
                    try:
                        await self.websocket.send_json(error_payload)
                    except RuntimeError as ws_err:
                        print(f"WebSocket already closed: {ws_err}")
                    except Exception as unexpected:
                        print(f"Unexpected WebSocket error: {unexpected}")
                else:
                    print("No websocket connected for error reporting.")

        if self.websocket:
            await self.websocket.send_json({ "closeConnection": True });
        return;



