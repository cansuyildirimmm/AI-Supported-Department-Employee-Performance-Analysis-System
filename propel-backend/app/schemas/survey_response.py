from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional

# Employee bilgisi
class EmployeeInSurvey(BaseModel):
    id: int
    position: Optional[str]
    user_id: int
    
    class Config:
        from_attributes = True

class SurveyResponseBase(BaseModel):
    employee_id: int
    survey_type: str = Field(..., description="motivation, satisfaction, stress")
    score: float = Field(..., ge=1, le=5, description="1-5 arası Likert ölçeği")
    period_date: date
    comments: Optional[str] = Field(None, max_length=500)

class SurveyResponseCreate(SurveyResponseBase):
    pass

class SurveyResponseUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=500)

class SurveyResponseResponse(SurveyResponseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Detaylı response (employee ilişkisiyle)
class SurveyResponseDetailResponse(SurveyResponseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    employee: EmployeeInSurvey
    
    class Config:
        from_attributes = True