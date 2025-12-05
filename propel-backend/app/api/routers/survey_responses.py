from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.survey_response import (
    SurveyResponseCreate, 
    SurveyResponseUpdate, 
    SurveyResponseResponse,
    SurveyResponseDetailResponse
)
from app.services.survey_service import SurveyService

router = APIRouter()

@router.post("/", response_model=SurveyResponseResponse, status_code=status.HTTP_201_CREATED)
def create_survey_response(
    survey_data: SurveyResponseCreate,
    db: Session = Depends(get_db)
):
    """
    Yeni anket cevabı oluştur
    
    - **employee_id**: Çalışan ID'si
    - **survey_type**: Anket tipi (motivation, satisfaction, stress)
    - **score**: Puan (1-5 arası)
    - **period_date**: Dönem tarihi
    - **comments**: Yorum (opsiyonel, max 500 karakter)
    """
    return SurveyService.create_survey_response(db, survey_data)

@router.get("/", response_model=List[SurveyResponseDetailResponse])
def list_survey_responses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Tüm anket cevaplarını listele"""
    return SurveyService.get_all_survey_responses(db, skip, limit)

@router.get("/{survey_id}", response_model=SurveyResponseDetailResponse)
def get_survey_response(
    survey_id: int,
    db: Session = Depends(get_db)
):
    """ID'ye göre anket cevabı getir"""
    return SurveyService.get_survey_response_by_id(db, survey_id)

@router.get("/employee/{emp_id}", response_model=List[SurveyResponseDetailResponse])
def get_responses_by_employee(
    emp_id: int,
    db: Session = Depends(get_db)
):
    """Çalışana göre anket cevaplarını listele"""
    return SurveyService.get_responses_by_employee(db, emp_id)

@router.get("/type/{survey_type}", response_model=List[SurveyResponseDetailResponse])
def get_responses_by_type(
    survey_type: str,
    db: Session = Depends(get_db)
):
    """
    Anket tipine göre cevapları listele
    
    - **survey_type**: motivation, satisfaction, stress
    """
    return SurveyService.get_responses_by_type(db, survey_type)

@router.get("/department/{dept_id}", response_model=List[SurveyResponseDetailResponse])
def get_responses_by_department(
    dept_id: int,
    db: Session = Depends(get_db)
):
    """Departmana göre anket cevaplarını listele"""
    return SurveyService.get_responses_by_department(db, dept_id)

@router.put("/{survey_id}", response_model=SurveyResponseResponse)
def update_survey_response(
    survey_id: int,
    survey_data: SurveyResponseUpdate,
    db: Session = Depends(get_db)
):
    """Anket cevabını güncelle"""
    return SurveyService.update_survey_response(db, survey_id, survey_data)

@router.delete("/{survey_id}")
def delete_survey_response(
    survey_id: int,
    db: Session = Depends(get_db)
):
    """Anket cevabını sil"""
    return SurveyService.delete_survey_response(db, survey_id)