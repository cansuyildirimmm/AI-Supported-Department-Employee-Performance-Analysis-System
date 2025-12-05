from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.db.models.user import UserRole
from app.db.models.employee import Employee
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.services.department_service import DepartmentService
from app.api.dependencies import get_current_user, get_current_active_admin
from app.db.models.user import User  # ✅ Model'den import et

router = APIRouter()

@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    dept_data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Yeni departman oluştur (Sadece Admin)
    
    - **name**: Departman adı (zorunlu, benzersiz)
    - **description**: Departman açıklaması (opsiyonel)
    """
    return DepartmentService.create_department(db, dept_data)

@router.get("/", response_model=List[DepartmentResponse])
def list_departments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Departmanları listele
    - Admin: Tüm departmanlar
    - Manager/Employee: Sadece kendi departmanı
    """
    # ✅ Admin ise tümünü göster
    if current_user.role == UserRole.admin:
        return DepartmentService.get_all_departments(db, skip, limit)
    
    # ✅ Manager veya Employee ise sadece kendi departmanı
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Çalışan kaydınız bulunamadı"
        )
    
    # Sadece kendi departmanını döndür
    return [DepartmentService.get_department_by_id(db, employee.department_id)]

@router.get("/{dept_id}", response_model=DepartmentResponse)
def get_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Departman detayı
    - Admin: Tüm departmanlar
    - Manager/Employee: Sadece kendi departmanı
    """
    department = DepartmentService.get_department_by_id(db, dept_id)
    
    # ✅ Admin değilse, sadece kendi departmanını görebilir
    if current_user.role != UserRole.admin:
        employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not employee or employee.department_id != dept_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu departmanı görüntüleme yetkiniz yok"
            )
    
    return department

@router.put("/{dept_id}", response_model=DepartmentResponse)
def update_department(
    dept_id: int,
    dept_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Departman güncelle (Sadece Admin)
    """
    return DepartmentService.update_department(db, dept_id, dept_data)

@router.delete("/{dept_id}")
def delete_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Departman sil (Sadece Admin, içinde çalışan yoksa)
    """
    return DepartmentService.delete_department(db, dept_id)