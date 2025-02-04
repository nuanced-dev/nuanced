from pydantic import BaseModel

class CodeRange(BaseModel):
    begin: int
    end: int

