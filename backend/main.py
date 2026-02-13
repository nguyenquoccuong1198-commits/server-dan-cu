from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- 1. CẤU HÌNH CƠ SỞ DỮ LIỆU (SUPABASE - POSTGRESQL) ---

# Đây là link kết nối đã ghép mật khẩu của bạn
DATABASE_URL = "postgresql://postgres.vokaxxmfssepxkxfenqa:AdminVietNam2026@aws-1-ap-southeast-1.supabase.co:5432/postgres"

# Tạo kết nối đến Supabase
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. ĐỊNH NGHĨA BẢNG DỮ LIỆU (Model) ---
class CuDanDB(Base):
    __tablename__ = "cu_dan"

    id = Column(Integer, primary_key=True, index=True)
    ten = Column(String, index=True)
    can_ho = Column(String)
    sdt = Column(String)

# Lệnh này sẽ tự động tạo bảng 'cu_dan' trên Supabase nếu chưa có
Base.metadata.create_all(bind=engine)

# --- 3. KHỞI TẠO APP FASTAPI ---
app = FastAPI()

# Cấu hình CORS (Để điện thoại và Web kết nối được)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hàm phụ trợ để lấy kết nối Database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 4. MÔ HÌNH DỮ LIỆU GIAO TIẾP (Pydantic) ---
class CuDanInput(BaseModel):
    ten: str
    can_ho: str
    sdt: str

# --- 5. CÁC API (CỬA NGÕ) ---

@app.get("/")
def home():
    return {"message": "Server đang chạy Online với Supabase!"}

@app.get("/api/cu-dan")
def lay_danh_sach_dan_cu(db: Session = Depends(get_db)):
    """Lấy toàn bộ danh sách từ Supabase"""
    danh_sach = db.query(CuDanDB).all()
    return danh_sach

@app.post("/api/them-cu-dan")
def them_cu_dan(nguoi: CuDanInput, db: Session = Depends(get_db)):
    """Thêm cư dân mới vào Supabase"""
    cu_dan_moi = CuDanDB(ten=nguoi.ten, can_ho=nguoi.can_ho, sdt=nguoi.sdt)
    
    db.add(cu_dan_moi)
    db.commit()
    db.refresh(cu_dan_moi)
    
    print(f"✅ Đã lưu lên Mây (Supabase): {nguoi.ten} - {nguoi.can_ho}")
    return {"message": "Thêm thành công", "data": cu_dan_moi}

@app.delete("/api/xoa-cu-dan/{user_id}")
def xoa_cu_dan(user_id: int, db: Session = Depends(get_db)):
    """Xóa cư dân"""
    cu_dan = db.query(CuDanDB).filter(CuDanDB.id == user_id).first()
    if cu_dan:
        db.delete(cu_dan)
        db.commit()
        return {"message": "Đã xóa thành công"}
    raise HTTPException(status_code=404, detail="Không tìm thấy cư dân")