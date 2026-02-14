from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ==================================================================================
# 1. CẤU HÌNH DATABASE (CHUẨN SUPABASE AWS-1 + SSL + KEEPALIVE)
# ==================================================================================

# Link kết nối đầy đủ (Đã bao gồm Driver psycopg2 và chế độ SSL)
DATABASE_URL = "postgresql+psycopg2://postgres.vokaxxmfssepxkxfenqa:AdminVietNam2026@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres?sslmode=require"

# Tạo Engine kết nối với các tham số tối ưu mạng
try:
    engine = create_engine(
        DATABASE_URL, 
        pool_pre_ping=True,  # Tự động kiểm tra kết nối sống/chết
        connect_args={
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }
    )
    # Thử kết nối ngay lập tức để in ra Log
    with engine.connect() as connection:
        print("✅ KẾT NỐI DATABASE THÀNH CÔNG (SSL MODE)!")
except Exception as e:
    print(f"❌ LỖI KẾT NỐI DATABASE: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================================================================================
# 2. ĐỊNH NGHĨA BẢNG DỮ LIỆU (Theo mẫu Phiếu Rà Soát)
# ==================================================================================
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

# Lệnh tạo bảng (Chỉ chạy nếu bảng chưa tồn tại)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"⚠️ Thông báo tạo bảng: {e}")

# ==================================================================================
# 3. KHỞI TẠO APP FASTAPI
# ==================================================================================
app = FastAPI()

# Cấu hình CORS (Cho phép mọi nơi truy cập - Quan trọng cho App điện thoại)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hàm lấy kết nối Database cho mỗi request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mô hình dữ liệu đầu vào (Validation)
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

# ==================================================================================
# 4. CÁC API (CỬA NGÕ GIAO TIẾP)
# ==================================================================================

@app.get("/")
def home():
    return {"message": "Server Dân Cư Online - Đã kích hoạt SSL!"}

@app.get("/api/danh-sach")
def lay_danh_sach(db: Session = Depends(get_db)):
    """Lấy toàn bộ danh sách phiếu đã nhập"""
    return db.query(PhieuKhaoSat).all()

@app.post("/api/gui-phieu")
def gui_phieu(form: PhieuInput, db: Session = Depends(get_db)):
    """Nhận phiếu từ App điện thoại và lưu vào Database"""
    try:
        # Tạo đối tượng mới từ dữ liệu gửi lên
        phieu_moi = PhieuKhaoSat(**form.dict())
        
        # Lưu vào Database
        db.add(phieu_moi)
        db.commit()
        db.refresh(phieu_moi)
        
        print(f"📝 Đã lưu phiếu của: {form.ho_ten}")
        return {"message": "Gửi thành công", "data": phieu_moi}
        
    except Exception as e:
        print(f"❌ Lỗi khi lưu phiếu: {e}")
        # Trả về lỗi 500 để App điện thoại biết đường báo lỗi
        raise HTTPException(status_code=500, detail=f"Lỗi Server: {str(e)}")