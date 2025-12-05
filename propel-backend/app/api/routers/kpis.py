from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.kpi import (
    KPICreate, KPIUpdate, KPIResponse,
    KPIRecordCreate, KPIRecordUpdate, KPIRecordResponse, KPIRecordDetailResponse
)
from app.services.kpi_service import KPIService

router = APIRouter()

# ==================== KPI Endpoints ====================

@router.post("/", response_model=KPIResponse, status_code=status.HTTP_201_CREATED)
def create_kpi(
    kpi_data: KPICreate,
    db: Session = Depends(get_db)
):
    """
    Yeni KPI (performans göstergesi) oluştur
    
    - **name**: KPI adı (örn: "Satış Hacmi", "Kod Satırı")
    - **description**: Açıklama
    - **unit**: Birim (numeric, percentage, currency, hours)
    - **department_id**: Departman ID (null = genel KPI)
    - **target_value**: Hedef değer (opsiyonel)
    """
    return KPIService.create_kpi(db, kpi_data)

@router.get("/", response_model=List[KPIResponse])
def list_kpis(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Tüm KPI'ları listele"""
    return KPIService.get_all_kpis(db, skip, limit)

@router.get("/{kpi_id}", response_model=KPIResponse)
def get_kpi(
    kpi_id: int,
    db: Session = Depends(get_db)
):
    """ID'ye göre KPI detayı getir"""
    return KPIService.get_kpi_by_id(db, kpi_id)

@router.get("/department/{dept_id}", response_model=List[KPIResponse])
def get_kpis_by_department(
    dept_id: int,
    db: Session = Depends(get_db)
):
    """Departmana göre KPI'ları listele"""
    return KPIService.get_kpis_by_department(db, dept_id)

@router.put("/{kpi_id}", response_model=KPIResponse)
def update_kpi(
    kpi_id: int,
    kpi_data: KPIUpdate,
    db: Session = Depends(get_db)
):
    """KPI güncelle"""
    return KPIService.update_kpi(db, kpi_id, kpi_data)

@router.delete("/{kpi_id}")
def delete_kpi(
    kpi_id: int,
    db: Session = Depends(get_db)
):
    """KPI sil (ilişkili kayıtlar yoksa)"""
    return KPIService.delete_kpi(db, kpi_id)

# ==================== KPI Record Endpoints ====================

@router.post("/records", response_model=KPIRecordResponse, status_code=status.HTTP_201_CREATED)
def create_kpi_record(
    record_data: KPIRecordCreate,
    db: Session = Depends(get_db)
):
    """
    Yeni KPI kaydı oluştur
    
    - **kpi_id**: KPI ID'si
    - **employee_id**: Çalışan ID'si
    - **value**: KPI değeri (örn: 4500 kod satırı, 85% başarı oranı)
    - **period_date**: Dönem tarihi (örn: 2025-01-01)
    """
    return KPIService.create_kpi_record(db, record_data)

@router.get("/records", response_model=List[KPIRecordDetailResponse])
def list_kpi_records(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Tüm KPI kayıtlarını listele (detaylı)"""
    return KPIService.get_all_kpi_records(db, skip, limit)

@router.get("/records/{record_id}", response_model=KPIRecordDetailResponse)
def get_kpi_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """ID'ye göre KPI kaydı getir"""
    return KPIService.get_kpi_record_by_id(db, record_id)

@router.get("/records/employee/{emp_id}", response_model=List[KPIRecordDetailResponse])
def get_records_by_employee(
    emp_id: int,
    db: Session = Depends(get_db)
):
    """Çalışana göre KPI kayıtlarını listele"""
    return KPIService.get_records_by_employee(db, emp_id)

@router.get("/records/kpi/{kpi_id}", response_model=List[KPIRecordDetailResponse])
def get_records_by_kpi(
    kpi_id: int,
    db: Session = Depends(get_db)
):
    """KPI'ya göre kayıtları listele"""
    return KPIService.get_records_by_kpi(db, kpi_id)

@router.put("/records/{record_id}", response_model=KPIRecordResponse)
def update_kpi_record(
    record_id: int,
    record_data: KPIRecordUpdate,
    db: Session = Depends(get_db)
):
    """KPI kaydını güncelle"""
    return KPIService.update_kpi_record(db, record_id, record_data)

@router.delete("/records/{record_id}")
def delete_kpi_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """KPI kaydını sil"""
    return KPIService.delete_kpi_record(db, record_id)