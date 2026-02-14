from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ==============================================================================
# 🔴 CẤU HÌNH MỚI: DÙNG CỔNG 5432 TRÊN POOLER (Session Mode)
# ==============================================================================
# Link này đảm bảo:
# 1. Chạy trên IPv4 (nhờ aws-1...pooler) -> Render thích điều này
# 2. Dùng cổng 5432 (Session) -> Python/SQLAlchemy thích điều này
DATABASE_URL = "postgresql://postgres.vokaxxmfssepxkxfenqa:AdminVietNam2026@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres"

# Tạo engine (Không cần SSL mode phức tạp nữa, để mặc định cho nhẹ)
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
except Exception as e:
    print(f"Lỗi tạo engine: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- ĐỊNH NGHĨA BẢNG ---
class PhieuKhaoSat(Base):
    __tablename__ = "phieu_khao_sat"
    id = Column(Integer, primary_key=True, index=True)
    ho_ten = Column(String)
    ngay_sinh = Column(String)
    gio_tinh = Column(String)
    thuong_tru = Column(String)
    noi_o_hien_tai = Column(String)
    so_cmnd = Column(String)
    ngay_cap = Column(String)
    noi_cap = Column(String)
    que_quan = Column(String)
    dan_toc = Column(String)
    ton_giao = Column(String)
    sdt = Column(String)
    nghe_nghiep = Column(String)

# Tạo bảng
try:
    Base.metadata.create_all(bind=engine)
except:
    pass

# --- APP ---
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

class PhieuInput(BaseModel):
    ho_ten: str
    ngay_sinh: str = ""
    gio_tinh: str = "Nam"
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

# --- API ---
@app.get("/")
def home():
    return {"message": "Server Dân Cư - Cổng 5432 OK!"}

@app.get("/api/danh-sach")
def lay_danh_sach(db: Session = Depends(get_db)):
    return db.query(PhieuKhaoSat).all()

@app.post("/api/gui-phieu")
def gui_phieu(form: PhieuInput, db: Session = Depends(get_db)):
    try:
        phieu_moi = PhieuKhaoSat(**form.dict())
        db.add(phieu_moi)
        db.commit()
        db.refresh(phieu_moi)
        return {"message": "Thành công", "data": phieu_moi}
    except Exception as e:
        print(f"Lỗi: {e}")
        raise HTTPException(status_code=500, detail="Lỗi Server")