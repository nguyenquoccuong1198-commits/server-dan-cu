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

# --- 2. ĐỊNH NGHĨA BẢNG DỮ LIỆU (FULL OPTION) ---
class HoSoDanCu(Base):
    __tablename__ = "hoso_dancu_final_v2" # Đổi tên bảng để tạo mới sạch sẽ
    id = Column(Integer, primary_key=True, index=True)
    nguoi_tao_sdt = Column(String)
    
    # Tab 1: Chủ hộ
    ho_ten = Column(String)
    ngay_sinh = Column(String)
    gioi_tinh = Column(String)
    so_cmnd = Column(String)
    ngay_cap = Column(String)
    noi_cap = Column(String)
    thuong_tru = Column(String)
    noi_o_hien_tai = Column(String)
    que_quan = Column(String)
    
    # Các trường hay bị thiếu
    trinh_do = Column(String) # Trình độ văn hóa
    dan_toc = Column(String)
    ton_giao = Column(String)
    sdt = Column(String)
    cong_viec = Column(String)

    # Tab 2: Thành viên (Lưu JSON)
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

# Input Model (Phải khớp với App điện thoại)
class HoSoInput(BaseModel):
    nguoi_tao_sdt: str = ""
    ho_ten: str
    ngay_sinh: str = ""
    gioi_tinh: str = ""
    so_cmnd: str = ""
    ngay_cap: str = ""
    noi_cap: str = ""
    thuong_tru: str = ""
    noi_o_hien_tai: str = ""
    que_quan: str = ""
    trinh_do: str = "" # Quan trọng
    dan_toc: str = ""
    ton_giao: str = ""
    sdt: str = ""
    cong_viec: str = ""
    danh_sach_thanh_vien: str = "[]"

# --- 4. API ---
@app.get("/")
def home(): return {"message": "Server Final V2 OK"}

@app.post("/api/dang-ky")
def dang_ky(user: dict, db: Session = Depends(get_db)):
    # (Giữ code đăng ký cũ hoặc trả về dummy nếu không dùng bảng user riêng)
    return {"message": "OK"}

@app.post("/api/dang-nhap")
def dang_nhap(form: dict, db: Session = Depends(get_db)):
    # Đăng nhập giả lập để test nhanh, hoặc dùng bảng User nếu cần
    return {"message": "OK", "ho_ten": "Cán bộ", "sdt": form.get("sdt")}

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