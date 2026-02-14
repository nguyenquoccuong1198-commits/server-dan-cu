from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import json

# --- 1. CẤU HÌNH DATABASE ---
# Giữ nguyên Link kết nối chuẩn của bạn
DATABASE_URL = "postgresql://postgres.vokaxxmfssepxkxfenqa:AdminVietNam2026@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres"

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
except Exception as e:
    print(f"Lỗi tạo engine: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. ĐỊNH NGHĨA BẢNG DỮ LIỆU (MỚI & ĐẦY ĐỦ) ---
class HoSoDanCu(Base):
    __tablename__ = "hoso_dancu_pro"  # Đổi tên bảng mới

    id = Column(Integer, primary_key=True, index=True)
    
    # --- THÔNG TIN NGƯỜI ĐẠI DIỆN (TAB 1) ---
    ho_ten = Column(String)
    ngay_sinh = Column(String)
    gioi_tinh = Column(String)
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
    cong_viec = Column(String) # Thất nghiệp/Có việc...

    # --- THÔNG TIN THÀNH VIÊN (TAB 2) ---
    # Chúng ta sẽ lưu danh sách thành viên dưới dạng chuỗi văn bản (JSON)
    # Ví dụ: "[{'ten': 'Con A', 'quan_he': 'Con'}, {'ten': 'Vo B', 'quan_he': 'Vợ'}]"
    danh_sach_thanh_vien = Column(Text) 

# Tạo bảng (Lệnh này sẽ tạo bảng mới)
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

# Dữ liệu đầu vào (Validation)
class HoSoInput(BaseModel):
    # Tab 1
    ho_ten: str
    ngay_sinh: str = ""
    gioi_tinh: str = "Nam"
    so_cmnd: str = ""
    ngay_cap: str = ""
    noi_cap: str = "Cục CS QLHC về TTXH - BCA"
    thuong_tru: str = ""
    noi_o_hien_tai: str = ""
    que_quan: str = ""
    trinh_do: str = ""
    dan_toc: str = "Kinh"
    ton_giao: str = "Không"
    sdt: str = ""
    cong_viec: str = "Đang có việc làm"
    
    # Tab 2 (Danh sách JSON)
    danh_sach_thanh_vien: str = "[]"

# --- API ---
@app.get("/")
def home(): return {"message": "Server Dân Cư PRO - Sẵn sàng!"}

@app.get("/api/danh-sach")
def lay_danh_sach(db: Session = Depends(get_db)):
    # Lấy danh sách và sắp xếp mới nhất lên đầu
    return db.query(HoSoDanCu).order_by(HoSoDanCu.id.desc()).all()

@app.post("/api/gui-phieu")
def gui_phieu(form: HoSoInput, db: Session = Depends(get_db)):
    try:
        hoso = HoSoDanCu(**form.dict())
        db.add(hoso)
        db.commit()
        db.refresh(hoso)
        return {"message": "Thành công", "data": hoso}
    except Exception as e:
        print(f"Lỗi: {e}")
        raise HTTPException(status_code=500, detail="Lỗi Server")