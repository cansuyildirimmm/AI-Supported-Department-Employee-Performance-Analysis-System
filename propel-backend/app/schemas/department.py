from pydantic import BaseModel
from datetime import datetime
from typing import Optional

#SHEMAS Görevi: API üzerinden gelen veriyi doğrular (örn: email formatı doğru mu, puan 1 ile 5 arasında mı?) ve yanıt olarak gönderilecek verinin yapısını belirler.
# user.py, employee.py vb.
#İçinde UserCreate, UserUpdate, UserResponse gibi modeller bulunur. Bu sayede API, sadece gereken bilgileri dışarıya açar (örn: hashed_password asla UserResponse içinde olmaz).
class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True