from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- 1. CẤU HÌNH ---
# Dán link Supabase của bạn vào đây (Link cũ vẫn dùng tốt)
DATABASE_URL = "postgresql://postgres.vokaxxmfssepxkxfenqa:AdminVietNam2026@aws-1-ap-southeast-1.supabase.co:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. ĐỊNH NGHĨA BẢNG DỮ LIỆU MỚI (Theo file Word) ---
class PhieuKhaoSat(Base):
    __tablename__ = "phieu_khao_sat"  # Tên bảng mới

    id = Column(Integer, primary_key=True, index=True)
    ho_ten = Column(String)
    ngay_sinh = Column(String)
    gioi_tinh = Column(String)
    thuong_tru = Column(String)
    noi_o_hien_tai = Column(String)
    so_cmnd = Column(String)
    ngay_cap = Column(String)
    noi_cap = Column(String)
    que_quan = Column(String)
    dan_toc = Column(String)
    ton_giao = Column(String)
    sdt = Column(String)
    nghe_nghiep = Column(String) # Thất nghiệp/Có việc/Hưu trí/Học sinh

# Tạo bảng mới tự động
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# --- 3. DỮ LIỆU ĐẦU VÀO ---
class PhieuInput(BaseModel):
    ho_ten: str
    ngay_sinh: str = ""
    gioi_tinh: str = "Nam"
    thuong_tru: str = ""
    noi_o_hien_tai: str = ""
    so_cmnd: str = ""
    ngay_cap: str = ""
    noi_cap: str = "Cục CS QLHC về TTXH"
    que_quan: str = ""
    dan_toc: str = "Kinh"
    ton_giao: str = "Không"
    sdt: str = ""
    nghe_nghiep: str = "Đang có việc làm"

# --- 4. CÁC API ---
@app.get("/")
def home(): return {"message": "Server Phiếu Khảo Sát Online"}

@app.get("/api/danh-sach")
def lay_danh_sach(db: Session = Depends(get_db)):
    return db.query(PhieuKhaoSat).all()

@app.post("/api/gui-phieu")
def gui_phieu(form: PhieuInput, db: Session = Depends(get_db)):
    phieu_moi = PhieuKhaoSat(**form.dict())
    db.add(phieu_moi)
    db.commit()
    db.refresh(phieu_moi)
    print(f"✅ Đã nhận phiếu của: {form.ho_ten}")
    return {"message": "Gửi thành công", "data": phieu_moi}