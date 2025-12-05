from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from datetime import date

from app.db.models.kpi import KPI, KPIRecord
from app.db.models.department import Department
from app.db.models.employee import Employee
from app.schemas.kpi import KPICreate, KPIUpdate, KPIRecordCreate, KPIRecordUpdate

class KPIService:
    
    # ==================== KPI CRUD ====================
    
    @staticmethod
    def create_kpi(db: Session, kpi_data: KPICreate) -> KPI:
        """Yeni KPI tanımı oluştur"""
        
        # Eğer department_id verilmişse, department var mı kontrol et
        if kpi_data.department_id is not None:
            department = db.query(Department).filter(Department.id == kpi_data.department_id).first()
            if not department:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Departman bulunamadı (ID: {kpi_data.department_id})"
                )
        
        # Aynı isimde KPI var mı kontrol et (aynı departmanda)
        existing = db.query(KPI).filter(
            KPI.name == kpi_data.name,
            KPI.department_id == kpi_data.department_id
        ).first()
        
        if existing:
            dept_name = existing.department.name if existing.department else "Genel"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{kpi_data.name}' isimli KPI zaten '{dept_name}' için tanımlı"
            )
        
        db_kpi = KPI(**kpi_data.dict())
        db.add(db_kpi)
        db.commit()
        db.refresh(db_kpi)
        return db_kpi
    
    @staticmethod
    def get_all_kpis(db: Session, skip: int = 0, limit: int = 100) -> List[KPI]:
        """Tüm KPI'ları listele"""
        return db.query(KPI).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_kpi_by_id(db: Session, kpi_id: int) -> KPI:
        """ID'ye göre KPI getir"""
        kpi = db.query(KPI).filter(KPI.id == kpi_id).first()
        if not kpi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"KPI bulunamadı (ID: {kpi_id})"
            )
        return kpi
    
    @staticmethod
    def get_kpis_by_department(db: Session, dept_id: int) -> List[KPI]:
        """Departmana göre KPI'ları listele"""
        department = db.query(Department).filter(Department.id == dept_id).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Departman bulunamadı (ID: {dept_id})"
            )
        
        return db.query(KPI).filter(KPI.department_id == dept_id).all()
    
    @staticmethod
    def update_kpi(db: Session, kpi_id: int, kpi_data: KPIUpdate) -> KPI:
        """KPI güncelle"""
        kpi = KPIService.get_kpi_by_id(db, kpi_id)
        
        # Eğer department_id değiştiriliyorsa kontrol et
        if kpi_data.department_id is not None:
            department = db.query(Department).filter(Department.id == kpi_data.department_id).first()
            if not department:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Departman bulunamadı (ID: {kpi_data.department_id})"
                )
        
        update_data = kpi_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(kpi, field, value)
        
        db.commit()
        db.refresh(kpi)
        return kpi
    
    @staticmethod
    def delete_kpi(db: Session, kpi_id: int) -> dict:
        """KPI sil"""
        kpi = KPIService.get_kpi_by_id(db, kpi_id)
        
        # KPI'ya ait kayıtlar varsa uyarı ver
        if kpi.records:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bu KPI'ya ait {len(kpi.records)} kayıt bulunuyor. Önce kayıtları silin."
            )
        
        db.delete(kpi)
        db.commit()
        return {"message": f"'{kpi.name}' KPI'sı başarıyla silindi"}
    
    # ==================== KPI Record CRUD ====================
    
    @staticmethod
    def create_kpi_record(db: Session, record_data: KPIRecordCreate) -> KPIRecord:
        """Yeni KPI kaydı oluştur"""
        
        # KPI var mı kontrol et
        kpi = db.query(KPI).filter(KPI.id == record_data.kpi_id).first()
        if not kpi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"KPI bulunamadı (ID: {record_data.kpi_id})"
            )
        
        # Employee var mı kontrol et
        employee = db.query(Employee).filter(Employee.id == record_data.employee_id).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Çalışan bulunamadı (ID: {record_data.employee_id})"
            )
        
        # KPI departmana özel mi? Öyleyse çalışan o departmanda mı?
        if kpi.department_id is not None and employee.department_id != kpi.department_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bu KPI '{kpi.department.name}' departmanına özel. Çalışan farklı departmanda."
            )
        
        # Aynı çalışan, aynı KPI, aynı dönem için kayıt var mı?
        existing = db.query(KPIRecord).filter(
            KPIRecord.kpi_id == record_data.kpi_id,
            KPIRecord.employee_id == record_data.employee_id,
            KPIRecord.period_date == record_data.period_date
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bu çalışan için bu KPI'da bu dönem zaten kayıt mevcut (ID: {existing.id})"
            )
        
        db_record = KPIRecord(**record_data.dict())
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    
    @staticmethod
    def get_all_kpi_records(db: Session, skip: int = 0, limit: int = 100) -> List[KPIRecord]:
        """Tüm KPI kayıtlarını listele"""
        return db.query(KPIRecord).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_kpi_record_by_id(db: Session, record_id: int) -> KPIRecord:
        """ID'ye göre KPI kaydı getir"""
        record = db.query(KPIRecord).filter(KPIRecord.id == record_id).first()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"KPI kaydı bulunamadı (ID: {record_id})"
            )
        return record
    
    @staticmethod
    def get_records_by_employee(db: Session, emp_id: int) -> List[KPIRecord]:
        """Çalışana göre KPI kayıtlarını listele"""
        employee = db.query(Employee).filter(Employee.id == emp_id).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Çalışan bulunamadı (ID: {emp_id})"
            )
        
        return db.query(KPIRecord).filter(KPIRecord.employee_id == emp_id).all()
    
    @staticmethod
    def get_records_by_kpi(db: Session, kpi_id: int) -> List[KPIRecord]:
        """KPI'ya göre kayıtları listele"""
        kpi = db.query(KPI).filter(KPI.id == kpi_id).first()
        if not kpi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"KPI bulunamadı (ID: {kpi_id})"
            )
        
        return db.query(KPIRecord).filter(KPIRecord.kpi_id == kpi_id).all()
    
    @staticmethod
    def update_kpi_record(db: Session, record_id: int, record_data: KPIRecordUpdate) -> KPIRecord:
        """KPI kaydını güncelle"""
        record = KPIService.get_kpi_record_by_id(db, record_id)
        
        update_data = record_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)
        
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def delete_kpi_record(db: Session, record_id: int) -> dict:
        """KPI kaydını sil"""
        record = KPIService.get_kpi_record_by_id(db, record_id)
        
        db.delete(record)
        db.commit()
        return {"message": f"KPI kaydı başarıyla silindi (ID: {record_id})"}