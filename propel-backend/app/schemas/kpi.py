from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from app.db.models.kpi import KPIUnit

# Department bilgisi (ilişkili)
class DepartmentInKPI(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

# Employee bilgisi (KPIRecord için)
class EmployeeInKPIRecord(BaseModel):
    id: int
    position: Optional[str]
    user_id: int
    
    class Config:
        from_attributes = True

# ==================== KPI ====================

class KPIBase(BaseModel):
    name: str
    description: Optional[str] = None
    unit: KPIUnit
    department_id: Optional[int] = None  # NULL = genel KPI
    target_value: Optional[float] = None

class KPICreate(KPIBase):
    pass

class KPIUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[KPIUnit] = None
    department_id: Optional[int] = None
    target_value: Optional[float] = None

class KPIResponse(KPIBase):
    id: int
    created_at: datetime
    updated_at: datetime
    department: Optional[DepartmentInKPI] = None
    
    class Config:
        from_attributes = True

# ==================== KPI Record ====================

class KPIRecordBase(BaseModel):
    kpi_id: int
    employee_id: int
    value: float
    period_date: date  # Hangi ay/dönem için

class KPIRecordCreate(KPIRecordBase):
    pass

class KPIRecordUpdate(BaseModel):
    value: Optional[float] = None
    period_date: Optional[date] = None

class KPIRecordResponse(KPIRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# İlişkilerle birlikte detaylı response
class KPIRecordDetailResponse(KPIRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime
    kpi: KPIResponse
    employee: EmployeeInKPIRecord
    
    class Config:
        from_attributes = True