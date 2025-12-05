from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.db.models.employee import Employee

#JWT Token'ı çözerek kullanıcının kim olduğunu ve hangi yetkiye sahip olduğunu kontrol eden bağımlılık (Dependency) fonksiyonlarını barındırır.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    """JWT token'dan mevcut kullanıcıyı al"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulanamadı",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kullanıcı hesabı aktif değil"
        )
    
    return user

def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    """Sadece Admin yetkisi kontrolü"""
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için Admin yetkisi gerekli"
        )
    return current_user

def get_current_manager_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Manager veya Admin yetkisi kontrolü"""
    if current_user.role not in [UserRole.admin, UserRole.department_manager]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için Manager veya Admin yetkisi gerekli"
        )
    return current_user

def get_current_employee_record(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Employee:
    """Mevcut kullanıcının employee kaydını getir"""
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu kullanıcının çalışan kaydı bulunamadı"
        )
    return employee