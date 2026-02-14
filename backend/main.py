from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import json

# --- 1. CẤU HÌNH DATABASE ---
DATABASE_URL = "postgresql://postgres.vokaxxmfssepxkxfenqa:AdminVietNam2026@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres"

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
except Exception as e:
    print(f"Lỗi tạo engine: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. ĐỊNH NGHĨA BẢNG DỮ LIỆU ---

# Bảng User (Để đăng nhập và lấy tên thật)
class User(Base):
    __tablename__ = "users_final_v2" 
    id = Column(Integer, primary_key=True, index=True)
    sdt = Column(String, unique=True, index=True)
    mat_khau = Column(String)
    ho_ten = Column(String)

# Bảng Hồ Sơ
class HoSoDanCu(Base):
    __tablename__ = "hoso_dancu_final_v3" # Đổi v3 để reset lại cột giới tính cho sạch
    id = Column(Integer, primary_key=True, index=True)
    nguoi_tao_sdt = Column(String)
    
    # Tab 1
    ho_ten = Column(String)
    ngay_sinh = Column(String)
    gioi_tinh = Column(String) # Server chờ 'gioi_tinh'
    so_cmnd = Column(String)
    ngay_cap = Column(String)
    noi_cap = Column(String)
    thuong_tru = Column(String)
    noi_o_hien_tai = Column(String)
    que_quan = Column(String)
    trinh_do = Column(String)
    dan_toc = Column(String)
    ton_giao = Column(String)
    sdt = Column(String)
    cong_viec = Column(String)

    # Tab 2
    danh_sach_thanh_vien = Column(Text) 

try:
    Base.metadata.create_all(bind=engine)
except:
    pass

# --- 3. APP FASTAPI ---
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# Models
class UserInput(BaseModel):
    sdt: str
    mat_khau: str
    ho_ten: str = ""

class LoginInput(BaseModel):
    sdt: str
    mat_khau: str

class HoSoInput(BaseModel):
    nguoi_tao_sdt: str = ""
    ho_ten: str
    ngay_sinh: str = ""
    gioi_tinh: str = "" # Quan trọng: Phải là 'gioi_tinh'
    so_cmnd: str = ""
    ngay_cap: str = ""
    noi_cap: str = ""
    thuong_tru: str = ""
    noi_o_hien_tai: str = ""
    que_quan: str = ""
    trinh_do: str = ""
    dan_toc: str = ""
    ton_giao: str = ""
    sdt: str = ""
    cong_viec: str = ""
    danh_sach_thanh_vien: str = "[]"

# --- API ---
@app.get("/")
def home(): return {"message": "Server V3 Online"}

@app.post("/api/dang-ky")
def dang_ky(user: UserInput, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.sdt == user.sdt).first()
    if db_user:
        raise HTTPException(status_code=400, detail="SĐT đã tồn tại")
    new_user = User(sdt=user.sdt, mat_khau=user.mat_khau, ho_ten=user.ho_ten)
    db.add(new_user)
    db.commit()
    return {"message": "Đăng ký thành công"}

@app.post("/api/dang-nhap")
def dang_nhap(form: LoginInput, db: Session = Depends(get_db)):
    # Tìm user trong database để lấy tên thật
    user = db.query(User).filter(User.sdt == form.sdt, User.mat_khau == form.mat_khau).first()
    if not user:
        raise HTTPException(status_code=400, detail="Sai SĐT hoặc mật khẩu")
    # Trả về tên thật của người dùng
    return {"message": "OK", "ho_ten": user.ho_ten, "sdt": user.sdt}

@app.get("/api/danh-sach")
def lay_danh_sach(db: Session = Depends(get_db)):
    return db.query(HoSoDanCu).order_by(HoSoDanCu.id.desc()).all()

@app.post("/api/gui-phieu")
def gui_phieu(form: HoSoInput, db: Session = Depends(get_db)):
    try:
        hoso = HoSoDanCu(**form.dict())
        db.add(hoso)
        db.commit()
        return {"message": "Thành công"}
    except Exception as e:
        print(f"Lỗi: {e}")
        raise HTTPException(status_code=500, detail=str(e))